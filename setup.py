#!/usr/bin/env python3
"""
Setup script for AI Competitor Monitor
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Please run: pip install -r requirements.txt")
        return False
    return True

def setup_chrome_driver():
    """Setup Chrome driver for Selenium"""
    system = platform.system().lower()
    print(f"🌐 Setting up Chrome driver for {system}...")
    
    if system == "linux":
        print("Installing Chrome/Chromium...")
        try:
            # Try to install chromium-browser
            subprocess.run(["sudo", "apt-get", "update"], check=False)
            subprocess.run(["sudo", "apt-get", "install", "-y", "chromium-browser"], check=False)
            print("✅ Chromium browser installed")
        except:
            print("⚠️  Please install Chrome/Chromium manually:")
            print("   sudo apt-get install chromium-browser")
    
    elif system == "darwin":  # macOS
        print("Please install Chrome manually from: https://www.google.com/chrome/")
        print("Or use Homebrew: brew install --cask google-chrome")
    
    elif system == "windows":
        print("Please install Chrome manually from: https://www.google.com/chrome/")
    
    print("📝 Chrome driver will be auto-downloaded by Selenium")

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return
    
    if env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created")
        print("🔑 Please edit .env with your API keys:")
        print("   - OPENAI_API_KEY (required)")
        print("   - SLACK_BOT_TOKEN (optional)")
        print("   - NOTION_TOKEN (optional)")
    else:
        print("❌ .env.example template not found")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["reports", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def verify_config_files():
    """Verify configuration files exist"""
    print("🔧 Verifying configuration files...")
    
    config_files = {
        "config.json": "System configuration",
        "targets.json": "Monitoring targets",
        ".env": "Environment variables"
    }
    
    for file, description in config_files.items():
        if Path(file).exists():
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - {description} (missing)")

def run_test_configuration():
    """Run configuration test"""
    print("\n🧪 Testing configuration...")
    try:
        result = subprocess.run([sys.executable, "cli.py", "test-config"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Configuration test passed")
        else:
            print("⚠️  Configuration test issues detected")
            print(result.stdout)
    except Exception as e:
        print(f"❌ Could not run configuration test: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup completed! Next steps:")
    print("="*60)
    
    print("\n1. 🔑 Configure API Keys:")
    print("   Edit .env file with your API keys")
    print("   - Get OpenAI API key: https://platform.openai.com/api-keys")
    print("   - Get Slack Bot Token: https://api.slack.com/apps")
    print("   - Get Notion Token: https://www.notion.so/my-integrations")
    
    print("\n2. 🎯 Review Monitoring Targets:")
    print("   python cli.py list-targets")
    print("   python cli.py add-target      # Add your competitors")
    
    print("\n3. 🧪 Test Your Setup:")
    print("   python cli.py test-config")
    
    print("\n4. 🚀 Run Your First Monitoring Cycle:")
    print("   python cli.py run")
    
    print("\n5. ⏰ Start Automated Monitoring:")
    print("   python competitor_monitor.py")
    
    print("\n📚 Documentation:")
    print("   Read README.md for detailed instructions")
    print("   Use 'python cli.py --help' for CLI commands")
    
    print("\n💡 Pro Tips:")
    print("   - Start with 3-5 competitors to test the system")
    print("   - Use weekly monitoring frequency initially")
    print("   - Monitor both direct and indirect competitors")
    print("   - Check the reports/ directory for generated reports")

def main():
    """Main setup function"""
    print("🚀 AI Competitor Monitor Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Setup Chrome driver
    setup_chrome_driver()
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Verify config files
    verify_config_files()
    
    # Test configuration (if possible)
    if Path(".env").exists() and Path("config.json").exists():
        run_test_configuration()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()