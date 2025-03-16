import streamlit as st
import os
import requests
import json
import time
from datetime import datetime
from modules.logger import Logger

class OpenAIBridge:
    def __init__(self, logger=None):
        # Initialize with Apps Script endpoint URL from environment variable
        self.apps_script_url = os.getenv('APPS_SCRIPT_URL', '')
        
        # Set up logger
        self.logger = logger if logger else Logger()
        
        # Request timeout in seconds
        self.timeout = 30
        
        # Maximum number of retries for API calls
        self.max_retries = 3
        
        # Initialize and log status
        if self.apps_script_url:
            self.logger.info(f"OpenAI bridge initialized with Apps Script URL")
        else:
            self.logger.warning("OpenAI bridge initialized without Apps Script URL - will use mock data")
    
    def analyze_website(self, url):
        """
        Analyze a website by making a request to the Google Apps Script endpoint
        that connects to OpenAI API.
        
        Args:
            url (str): The URL of the website to analyze
            
        Returns:
            dict: Analysis results with status, confidence, and details
        """
        if not url:
            self.logger.error("Empty URL provided to analyze_website")
            return {
                'success': False,
                'message': 'No URL provided for analysis'
            }
        
        self.logger.info(f"Analyzing website: {url}")
        
        # If no Apps Script URL is configured, use mock data
        if not self.apps_script_url:
            self.logger.warning(f"No Apps Script URL configured, using mock data for {url}")
            return self._mock_website_analysis(url)
        
        # Try to call the Apps Script endpoint
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.logger.debug(f"Attempt {retry_count + 1} to call Apps Script endpoint")
                
                # Prepare the request data
                payload = {
                    'action': 'analyzeWebsite',
                    'url': url
                }
                
                # Make the request to the Apps Script endpoint
                response = requests.post(
                    self.apps_script_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                # Check for HTTP error status codes
                if response.status_code != 200:
                    self.logger.error(f"Error response from Apps Script: {response.status_code} - {response.text}")
                    
                    # If we got a 5xx error, retry
                    if 500 <= response.status_code < 600 and retry_count < self.max_retries - 1:
                        retry_count += 1
                        time.sleep(1)  # Wait before retrying
                        continue
                    
                    return {
                        'success': False,
                        'message': f'Error from Apps Script API: {response.status_code} - {response.text}'
                    }
                
                # Try to parse the response as JSON
                try:
                    result = response.json()
                    self.logger.info(f"Successfully analyzed website {url}: {result.get('status', 'UNKNOWN')}")
                    return result
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON response from Apps Script: {e}")
                    return {
                        'success': False,
                        'message': f'Invalid response format from Apps Script: {str(e)}'
                    }
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout while calling Apps Script endpoint (attempt {retry_count + 1})")
                retry_count += 1
                
                # Only retry if we haven't exceeded max retries
                if retry_count >= self.max_retries:
                    self.logger.error(f"Max retries exceeded for website {url}")
                    return {
                        'success': False,
                        'message': 'Timeout while connecting to Apps Script endpoint'
                    }
                
                # Exponential backoff
                time.sleep(2 ** retry_count)
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error connecting to Apps Script endpoint: {str(e)}")
                return {
                    'success': False,
                    'message': f'Error connecting to Apps Script endpoint: {str(e)}'
                }
        
        # If we get here, all retries failed
        self.logger.error(f"All attempts to analyze website {url} failed")
        return {
            'success': False,
            'message': 'Failed to analyze website after multiple attempts'
        }
    
    def test_connection(self):
        """
        Test the connection to the Apps Script endpoint.
        
        Returns:
            dict: Test result with success flag and message
        """
        if not self.apps_script_url:
            return {
                'success': False,
                'message': 'No Apps Script URL configured'
            }
        
        try:
            self.logger.info("Testing connection to Apps Script endpoint")
            response = requests.post(
                self.apps_script_url,
                json={'action': 'testConnection'},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Connection successful'
                }
            else:
                return {
                    'success': False,
                    'message': f'Connection failed with status code {response.status_code}: {response.text}'
                }
        except Exception as e:
            self.logger.error(f"Error testing connection: {str(e)}")
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }
    
    def _mock_website_analysis(self, url):
        """
        Generate mock website analysis for demonstration or when API is unavailable.
        
        Args:
            url (str): The URL that would be analyzed
            
        Returns:
            dict: Mock analysis results
        """
        self.logger.debug(f"Generating mock analysis for {url}")
        
        # In a real implementation, this would call the OpenAI API via Apps Script
        import random
        statuses = ['ACCEPTING', 'NOT_ACCEPTING', 'UNKNOWN']
        status = random.choice(statuses)
        
        # Generate consistent mock data based on the URL to make testing more realistic
        # This ensures the same URL always returns the same status
        url_hash = sum(ord(c) for c in url) % 3
        if url_hash == 0:
            status = 'ACCEPTING'
        elif url_hash == 1:
            status = 'NOT_ACCEPTING'
        else:
            status = 'UNKNOWN'
        
        self.logger.info(f"Mock analysis for {url}: {status}")
        
        return {
            'success': True,
            'status': status,
            'confidence': random.randint(50, 95),
            'details': {
                'waitingList': True if status == 'NOT_ACCEPTING' else False,
                'conditions': ['Alleen inwoners van postcodegebied'] if random.random() > 0.5 else [],
                'waitingTime': 'Ongeveer 3-6 maanden' if status == 'NOT_ACCEPTING' else None,
                'contactInfo': 'info@example.com' if random.random() > 0.3 else None,
                'lastUpdated': datetime.now().isoformat()
            },
            'reasoning': f"Website analysis indicates practice is {status.lower().replace('_', ' ')} new patients",
            'url': url,
            'timestamp': datetime.now().isoformat()
        }
