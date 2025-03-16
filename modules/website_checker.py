import streamlit as st
import os
import requests
import json
from datetime import datetime
import uuid
from modules.openai_bridge import OpenAIBridge

class WebsiteChecker:
    def __init__(self, data_layer):
        self.data_layer = data_layer
        self.openai_bridge = OpenAIBridge()
    
    def check_single_website(self, url, user_id, practice_id=None):
        """Check a single website for its status regarding accepting new patients"""
        try:
            # If practice_id is provided, get the practice first
            practice = None
            if practice_id:
                practice = self.data_layer.get_practice_by_id(practice_id)
                if not practice:
                    return {
                        'success': False,
                        'message': 'Practice not found'
                    }
            
            # Call the OpenAI bridge to analyze the website
            analysis_result = self.openai_bridge.analyze_website(url)
            
            if 'success' in analysis_result and analysis_result['success'] == False:
                return analysis_result
            
            # Store check result
            check_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            check_data = {
                'checkId': check_id,
                'practiceId': practice_id if practice_id else None,
                'timestamp': timestamp,
                'status': analysis_result['status'],
                'previousStatus': practice['status'] if practice else None,
                'details': json.dumps(analysis_result['details']),
                'notificationSent': False
            }
            
            # Update practice status if needed
            if practice and practice['status'] != analysis_result['status']:
                # Status has changed
                practice_updates = {
                    'status': analysis_result['status'],
                    'lastChecked': timestamp,
                    'lastStatusChange': timestamp,
                    'details': json.dumps(analysis_result['details'])
                }
                self.data_layer.update_practice(practice_id, practice_updates)
                
                # Send notification if status changed to ACCEPTING
                if analysis_result['status'] == 'ACCEPTING' and practice['status'] != 'ACCEPTING':
                    user = self.data_layer.get_user_by_id(user_id)
                    if user and user['settings'].get('emailNotifications', True):
                        # This would call the email service in a real implementation
                        # For now, just mark the notification as sent
                        check_data['notificationSent'] = True
            elif practice:
                # No status change, just update lastChecked
                self.data_layer.update_practice(practice_id, {
                    'lastChecked': timestamp
                })
            
            # Return result
            return {
                'success': True,
                'status': analysis_result['status'],
                'previousStatus': practice['status'] if practice else None,
                'statusChanged': practice and practice['status'] != analysis_result['status'],
                'details': analysis_result['details'],
                'timestamp': timestamp
            }
            
        except Exception as e:
            print(f"Error checking website {url}: {str(e)}")
            return {
                'success': False,
                'message': f'Error checking website: {str(e)}'
            }
    
    def check_all_user_websites(self, user_id):
        """Check all websites for a user"""
        try:
            # Get all practices for the user
            practices = self.data_layer.get_practices_by_user(user_id)
            if not practices:
                return {
                    'success': True,
                    'message': 'No practices found for user',
                    'totalChecked': 0,
                    'statusChanges': 0
                }
            
            # Check each practice
            total_checked = 0
            status_changes = 0
            errors = []
            
            for practice in practices:
                result = self.check_single_website(
                    practice['websiteUrl'],
                    user_id,
                    practice['practiceId']
                )
                total_checked += 1
                
                if result.get('success'):
                    if result.get('statusChanged'):
                        status_changes += 1
                else:
                    errors.append({
                        'practiceId': practice['practiceId'],
                        'name': practice['name'],
                        'error': result.get('message', 'Unknown error')
                    })
            
            return {
                'success': True,
                'message': f'Checked {total_checked} practices, {status_changes} status changes',
                'totalChecked': total_checked,
                'statusChanges': status_changes,
                'errors': errors
            }
            
        except Exception as e:
            print(f"Error checking all websites for user {user_id}: {str(e)}")
            return {
                'success': False,
                'message': f'Error checking websites: {str(e)}'
            }