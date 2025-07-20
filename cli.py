#!/usr/bin/env python3
"""
CLI tool for managing the AI Competitor Monitor
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from competitor_monitor import AICompetitorMonitor, CompetitorTarget


def load_targets():
    """Load targets from targets.json"""
    try:
        with open('targets.json', 'r') as f:
            targets_data = json.load(f)
            return [CompetitorTarget(**target) for target in targets_data]
    except FileNotFoundError:
        print("❌ targets.json not found. Please create it first.")
        return []


def add_target():
    """Add a new competitor target"""
    print("🎯 Adding new competitor target")
    
    name = input("Company name: ").strip()
    if not name:
        print("❌ Company name is required")
        return
    
    website_url = input("Website URL: ").strip()
    if not website_url:
        print("❌ Website URL is required")
        return
    
    changelog_url = input("Changelog URL (optional): ").strip() or None
    pricing_url = input("Pricing URL (optional): ").strip() or None
    blog_url = input("Blog URL (optional): ").strip() or None
    
    # Social URLs
    social_urls = []
    print("Social URLs (press Enter when done):")
    while True:
        social_url = input("  Social URL: ").strip()
        if not social_url:
            break
        social_urls.append(social_url)
    
    # App Store URLs
    ios_url = input("iOS App Store URL (optional): ").strip() or None
    android_url = input("Android App Store URL (optional): ").strip() or None
    app_store_urls = {}
    if ios_url:
        app_store_urls["ios"] = ios_url
    if android_url:
        app_store_urls["android"] = android_url
    
    # RSS feeds
    rss_feeds = []
    print("RSS feed URLs (press Enter when done):")
    while True:
        rss_url = input("  RSS URL: ").strip()
        if not rss_url:
            break
        rss_feeds.append(rss_url)
    
    # Create target
    target = CompetitorTarget(
        name=name,
        website_url=website_url,
        changelog_url=changelog_url,
        pricing_url=pricing_url,
        blog_url=blog_url,
        social_urls=social_urls if social_urls else None,
        app_store_urls=app_store_urls if app_store_urls else None,
        rss_feeds=rss_feeds if rss_feeds else None
    )
    
    # Load existing targets
    try:
        with open('targets.json', 'r') as f:
            existing_targets = json.load(f)
    except FileNotFoundError:
        existing_targets = []
    
    # Add new target
    existing_targets.append(target.__dict__)
    
    # Save updated targets
    with open('targets.json', 'w') as f:
        json.dump(existing_targets, f, indent=2)
    
    print(f"✅ Added {name} to monitoring targets")


def list_targets():
    """List all competitor targets"""
    targets = load_targets()
    if not targets:
        print("📋 No targets configured")
        return
    
    print(f"📋 {len(targets)} competitor targets configured:")
    print("-" * 60)
    
    for i, target in enumerate(targets, 1):
        print(f"{i}. {target.name}")
        print(f"   Website: {target.website_url}")
        if target.changelog_url:
            print(f"   Changelog: {target.changelog_url}")
        if target.pricing_url:
            print(f"   Pricing: {target.pricing_url}")
        if target.social_urls:
            print(f"   Social: {', '.join(target.social_urls)}")
        print()


def remove_target():
    """Remove a competitor target"""
    targets = load_targets()
    if not targets:
        print("📋 No targets configured")
        return
    
    print("🗑️  Remove competitor target:")
    list_targets()
    
    try:
        choice = int(input("Enter target number to remove: ")) - 1
        if 0 <= choice < len(targets):
            target_name = targets[choice].name
            
            # Load existing targets as dict
            with open('targets.json', 'r') as f:
                existing_targets = json.load(f)
            
            # Remove target
            del existing_targets[choice]
            
            # Save updated targets
            with open('targets.json', 'w') as f:
                json.dump(existing_targets, f, indent=2)
            
            print(f"✅ Removed {target_name} from monitoring targets")
        else:
            print("❌ Invalid target number")
    except (ValueError, IndexError):
        print("❌ Invalid input")


async def run_monitor():
    """Run the monitoring system once"""
    print("🕵️ Running competitor monitoring...")
    
    monitor = AICompetitorMonitor()
    
    try:
        results = await monitor.run_monitoring_cycle()
        
        if results:
            print(f"✅ Monitoring completed. {len(results)} results collected.")
            
            # Generate summary
            summary = monitor.generate_weekly_summary(results)
            
            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/monitor_run_{timestamp}.md"
            Path("reports").mkdir(exist_ok=True)
            
            with open(filename, 'w') as f:
                f.write(f"# Competitor Monitoring Run\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(summary)
            
            print(f"📄 Report saved to {filename}")
            
            # Send notifications if configured
            notification_channels = monitor.config.get('notification_channels', [])
            
            if 'slack' in notification_channels and monitor.slack_client:
                await monitor.send_to_slack(summary, results)
                print("📤 Sent to Slack")
            
            if 'notion' in notification_channels and monitor.notion_client:
                await monitor.send_to_notion(summary, results)
                print("📤 Sent to Notion")
        else:
            print("⚠️  No results collected during monitoring")
            
    except Exception as e:
        print(f"❌ Monitoring failed: {str(e)}")


def test_config():
    """Test the configuration"""
    print("🔧 Testing configuration...")
    
    # Check required files
    required_files = ['config.json', 'targets.json']
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
    
    # Test API connections
    try:
        monitor = AICompetitorMonitor()
        
        # Test OpenAI
        if monitor.openai_client:
            print("✅ OpenAI client initialized")
        else:
            print("❌ OpenAI client failed to initialize")
        
        # Test Slack
        if monitor.slack_client:
            print("✅ Slack client initialized")
        else:
            print("⚠️  Slack client not configured (optional)")
        
        # Test Notion
        if monitor.notion_client:
            print("✅ Notion client initialized")
        else:
            print("⚠️  Notion client not configured (optional)")
        
        # Test targets
        targets = monitor.targets
        print(f"✅ {len(targets)} targets loaded")
        
        print("\n🎯 Configuration test completed")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")


def show_status():
    """Show system status"""
    print("📊 Competitor Monitor Status")
    print("-" * 40)
    
    # Check if system is running
    print("🔄 Scheduler: Not running (use 'python competitor_monitor.py' to start)")
    
    # Show last run
    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.md"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 Latest report: {latest_report.name}")
            print(f"   Created: {datetime.fromtimestamp(latest_report.stat().st_mtime)}")
        else:
            print("📄 No reports found")
    else:
        print("📄 No reports directory found")
    
    # Show targets
    targets = load_targets()
    print(f"🎯 Targets: {len(targets)} configured")
    
    # Show historical data
    if Path("historical_data.json").exists():
        try:
            with open("historical_data.json", 'r') as f:
                data = json.load(f)
                print(f"💾 Historical data: {len(data)} entries")
        except:
            print("💾 Historical data: Error reading file")
    else:
        print("💾 Historical data: No data file found")


def main():
    parser = argparse.ArgumentParser(description="AI Competitor Monitor CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add target command
    subparsers.add_parser('add-target', help='Add a new competitor target')
    
    # List targets command
    subparsers.add_parser('list-targets', help='List all competitor targets')
    
    # Remove target command
    subparsers.add_parser('remove-target', help='Remove a competitor target')
    
    # Run monitor command
    subparsers.add_parser('run', help='Run monitoring cycle once')
    
    # Test config command
    subparsers.add_parser('test-config', help='Test configuration and API connections')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'add-target':
        add_target()
    elif args.command == 'list-targets':
        list_targets()
    elif args.command == 'remove-target':
        remove_target()
    elif args.command == 'run':
        asyncio.run(run_monitor())
    elif args.command == 'test-config':
        test_config()
    elif args.command == 'status':
        show_status()


if __name__ == "__main__":
    main()