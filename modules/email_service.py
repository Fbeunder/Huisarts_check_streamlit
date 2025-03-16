import streamlit as st
import os

class EmailService:
    def __init__(self, data_layer):
        self.data_layer = data_layer
    
    def send_status_change_notification(self, user, practice, check_result):
        """Send a notification email for a status change"""
        # In this Streamlit version, we're just logging the notification
        # In a real implementation, this would send an actual email
        print(f"Would send email to {user['email']} about status change for practice {practice['name']}")
        return True