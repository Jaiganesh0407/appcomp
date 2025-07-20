#!/usr/bin/env python3
"""
Test script for AI Competitor Monitor
"""

import asyncio
import json
import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        'requests',
        'beautifulsoup4',
        'openai',
        'selenium',
        'feedparser',
        'schedule',
        'slack_sdk',
        'notion_client',
        'pandas',
        'python_dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            if module == 'beautifulsoup4':
                import bs4
            elif module == 'python_dotenv':
                import dotenv
            else:
                __import__(module.replace('-', '_'))
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful")
    return True

def test_config_files():
    """Test configuration files"""
    print("\n🔧 Testing configuration files...")
    
    # Test config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✅ config.json - valid JSON")
        
        required_keys = ['monitoring_frequency', 'ai_model', 'notification_channels']
        for key in required_keys:
            if key in config:
                print(f"✅ config.json has {key}")
            else:
                print(f"⚠️  config.json missing {key}")
                
    except FileNotFoundError:
        print("❌ config.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ config.json invalid JSON")
        return False
    
    # Test targets.json
    try:
        with open('targets.json', 'r') as f:
            targets = json.load(f)
        print("✅ targets.json - valid JSON")
        print(f"✅ {len(targets)} targets configured")
        
        for target in targets:
            if 'name' in target and 'website_url' in target:
                print(f"✅ Target: {target['name']}")
            else:
                print(f"⚠️  Invalid target: {target}")
                
    except FileNotFoundError:
        print("❌ targets.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ targets.json invalid JSON")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔑 Testing environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        if openai_key.startswith('sk-'):
            print("✅ OPENAI_API_KEY configured")
        else:
            print("⚠️  OPENAI_API_KEY format looks incorrect")
    else:
        print("❌ OPENAI_API_KEY not configured")
        return False
    
    # Check optional integrations
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if slack_token:
        if slack_token.startswith('xoxb-'):
            print("✅ SLACK_BOT_TOKEN configured")
        else:
            print("⚠️  SLACK_BOT_TOKEN format looks incorrect")
    else:
        print("⚠️  SLACK_BOT_TOKEN not configured (optional)")
    
    notion_token = os.getenv('NOTION_TOKEN')
    if notion_token:
        if notion_token.startswith('secret_'):
            print("✅ NOTION_TOKEN configured")
        else:
            print("⚠️  NOTION_TOKEN format looks incorrect")
    else:
        print("⚠️  NOTION_TOKEN not configured (optional)")
    
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 Testing OpenAI connection...")
    
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        if "test successful" in response.choices[0].message.content.lower():
            print("✅ OpenAI API connection successful")
            return True
        else:
            print("⚠️  OpenAI API responded but with unexpected content")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_selenium():
    """Test Selenium WebDriver"""
    print("\n🌐 Testing Selenium WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # Test with a simple page
        driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
        
        if "Test" in driver.page_source:
            print("✅ Selenium WebDriver working")
            driver.quit()
            return True
        else:
            print("⚠️  Selenium WebDriver loaded but content issue")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Selenium WebDriver failed: {e}")
        print("💡 Try installing: sudo apt-get install chromium-browser")
        return False

async def test_scraping():
    """Test web scraping functionality"""
    print("\n🕷️  Testing web scraping...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Test with a simple page
        response = requests.get("https://httpbin.org/html", timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if soup.find('h1'):
            print("✅ Web scraping with requests working")
            return True
        else:
            print("⚠️  Web scraping loaded but parsing issue")
            return False
            
    except Exception as e:
        print(f"❌ Web scraping failed: {e}")
        return False

def test_directories():
    """Test that required directories exist"""
    print("\n📁 Testing directories...")
    
    directories = ['reports', 'logs']
    
    for directory in directories:
        path = Path(directory)
        if path.exists() and path.is_dir():
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"⚠️  {directory}/ directory missing - creating...")
            path.mkdir(exist_ok=True)
    
    return True

async def test_full_system():
    """Test the full monitoring system (without API calls)"""
    print("\n🚀 Testing full system integration...")
    
    try:
        # Import the main module
        from competitor_monitor import AICompetitorMonitor
        
        # Initialize (but don't run)
        monitor = AICompetitorMonitor()
        
        print("✅ AICompetitorMonitor initialized")
        print(f"✅ {len(monitor.targets)} targets loaded")
        print(f"✅ Configuration loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Full system test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 AI Competitor Monitor - System Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Config Files", test_config_files),
        ("Environment", test_environment),
        ("Directories", test_directories),
        ("OpenAI Connection", test_openai_connection),
        ("Selenium", test_selenium),
        ("Web Scraping", lambda: asyncio.run(test_scraping())),
        ("Full System", lambda: asyncio.run(test_full_system()))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Edit .env with your API keys")
        print("   2. Run: python cli.py test-config")
        print("   3. Run: python cli.py run")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        print("\n💡 Common fixes:")
        print("   - Run: pip install -r requirements.txt")
        print("   - Install Chrome: sudo apt-get install chromium-browser")
        print("   - Configure .env file with valid API keys")

if __name__ == "__main__":
    asyncio.run(main())