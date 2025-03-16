import streamlit as st
import os
import uuid

class AuthService:
    def __init__(self, data_layer):
        self.data_layer = data_layer
    
    def get_user_by_email(self, email):
        """Get a user by email"""
        return self.data_layer.get_user_by_email(email)
    
    def create_user(self, email):
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user = {
            'userId': user_id,
            'email': email,
            'isActive': True,
            'isAdmin': False,
            'settings': {
                'emailNotifications': True,
                'notificationFrequency': 'immediately'
            }
        }
        return self.data_layer.create_user(user)
    
    def update_user_settings(self, user_id, settings):
        """Update user settings"""
        return self.data_layer.update_user(user_id, {'settings': settings})
    
    def create_emergency_admin(self, email):
        """Create an emergency admin user"""
        user_id = str(uuid.uuid4())
        user = {
            'userId': user_id,
            'email': email,
            'isActive': True,
            'isAdmin': True,
            'settings': {
                'emailNotifications': True,
                'notificationFrequency': 'immediately'
            }
        }
        return self.data_layer.create_user(user)