#!/usr/bin/env python3
"""
Test script voor de OpenAI bridge module.
Dit script test de verbinding met het Google Apps Script endpoint.

Gebruik:
python test_openai_bridge.py [URL]

Als URL is opgegeven, wordt deze geanalyseerd. Anders wordt alleen de verbinding getest.
"""

import os
import sys
import json
from dotenv import load_dotenv
from modules.openai_bridge import OpenAIBridge
from modules.logger import Logger

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize logger
    logger = Logger()
    logger.info("Starting OpenAI bridge test")
    
    # Initialize the OpenAI bridge
    bridge = OpenAIBridge(logger=logger)
    
    # Check if Apps Script URL is configured
    apps_script_url = os.getenv('APPS_SCRIPT_URL', '')
    if not apps_script_url:
        logger.error("APPS_SCRIPT_URL is not configured in .env file")
        print("\nError: APPS_SCRIPT_URL is not configured in .env file.")
        print("Please add the APPS_SCRIPT_URL to your .env file and try again.")
        sys.exit(1)
    
    # Test connection to Apps Script endpoint
    print("\nTesting connection to Apps Script endpoint...")
    result = bridge.test_connection()
    
    if result['success']:
        print(f"✅ Connection successful: {result['message']}")
    else:
        print(f"❌ Connection failed: {result['message']}")
        print("\nPlease check your APPS_SCRIPT_URL in the .env file and make sure the Apps Script is deployed and accessible.")
        sys.exit(1)
    
    # If URL is provided as argument, analyze it
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"\nAnalyzing website: {url}...")
        analysis = bridge.analyze_website(url)
        
        if analysis.get('success', False) or 'status' in analysis:
            print("\n✅ Website analysis result:")
            print(json.dumps(analysis, indent=2))
        else:
            print(f"\n❌ Website analysis failed: {analysis.get('message', 'Unknown error')}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()
