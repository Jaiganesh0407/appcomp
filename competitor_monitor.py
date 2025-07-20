import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from openai import OpenAI
from slack_sdk import WebClient
from notion_client import Client as NotionClient
import schedule
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('competitor_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CompetitorTarget:
    name: str
    website_url: str
    changelog_url: Optional[str] = None
    pricing_url: Optional[str] = None
    blog_url: Optional[str] = None
    social_urls: Optional[List[str]] = None
    app_store_urls: Optional[Dict[str, str]] = None  # {"ios": "url", "android": "url"}
    rss_feeds: Optional[List[str]] = None
    
@dataclass
class MonitoringResult:
    timestamp: datetime
    target_name: str
    content_type: str  # website, changelog, pricing, blog, social, app_store
    url: str
    content_hash: str
    raw_content: str
    ai_summary: str
    detected_changes: List[str]
    metadata: Dict[str, Any]

class AICompetitorMonitor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN')) if os.getenv('SLACK_BOT_TOKEN') else None
        self.notion_client = NotionClient(auth=os.getenv('NOTION_TOKEN')) if os.getenv('NOTION_TOKEN') else None
        
        # Configuration
        self.config = self._load_config()
        self.targets = self._load_targets()
        self.historical_data = self._load_historical_data()
        
        # Initialize web driver options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
    def _load_config(self) -> Dict:
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "monitoring_frequency": "weekly",
                "ai_model": "gpt-4",
                "max_content_length": 5000,
                "timeout": 30,
                "enable_selenium": True,
                "notification_channels": ["slack", "notion"],
                "changelog_keywords": ["release", "update", "new", "feature", "version"],
                "pricing_keywords": ["price", "pricing", "cost", "plan", "subscription"]
            }
    
    def _load_targets(self) -> List[CompetitorTarget]:
        """Load competitor targets from targets.json"""
        try:
            with open('targets.json', 'r') as f:
                targets_data = json.load(f)
                return [CompetitorTarget(**target) for target in targets_data]
        except FileNotFoundError:
            logger.warning("targets.json not found. Using default targets.")
            return self._get_default_targets()
    
    def _get_default_targets(self) -> List[CompetitorTarget]:
        """Default competitor targets for demonstration"""
        return [
            CompetitorTarget(
                name="Notion",
                website_url="https://www.notion.so",
                changelog_url="https://www.notion.so/releases",
                pricing_url="https://www.notion.so/pricing",
                blog_url="https://www.notion.so/blog",
                social_urls=["https://twitter.com/notionhq"],
                app_store_urls={
                    "ios": "https://apps.apple.com/app/notion-notes-docs-tasks/id1232780281",
                    "android": "https://play.google.com/store/apps/details?id=notion.id"
                }
            ),
            CompetitorTarget(
                name="Airtable",
                website_url="https://www.airtable.com",
                changelog_url="https://support.airtable.com/docs/whats-new",
                pricing_url="https://www.airtable.com/pricing",
                blog_url="https://blog.airtable.com",
                social_urls=["https://twitter.com/airtable"]
            )
        ]
    
    def _load_historical_data(self) -> Dict:
        """Load historical monitoring data"""
        try:
            with open('historical_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_historical_data(self):
        """Save historical monitoring data"""
        with open('historical_data.json', 'w') as f:
            json.dump(self.historical_data, f, indent=2, default=str)
    
    async def scrape_website_content(self, url: str, use_selenium: bool = False) -> str:
        """Scrape content from a website"""
        try:
            if use_selenium and self.config.get('enable_selenium', True):
                return await self._scrape_with_selenium(url)
            else:
                return await self._scrape_with_requests(url)
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return ""
    
    async def _scrape_with_requests(self, url: str) -> str:
        """Scrape using requests and BeautifulSoup"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=self.config.get('timeout', 30))
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Limit content length
        max_length = self.config.get('max_content_length', 5000)
        return text[:max_length] if len(text) > max_length else text
    
    async def _scrape_with_selenium(self, url: str) -> str:
        """Scrape using Selenium for dynamic content"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            
            # Limit content length
            max_length = self.config.get('max_content_length', 5000)
            return text[:max_length] if len(text) > max_length else text
            
        except Exception as e:
            logger.error(f"Selenium scraping failed for {url}: {str(e)}")
            return ""
        finally:
            if driver:
                driver.quit()
    
    async def scrape_rss_feeds(self, feed_urls: List[str]) -> List[Dict]:
        """Scrape RSS feeds for recent updates"""
        all_entries = []
        
        for feed_url in feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                
                # Get entries from the last week
                one_week_ago = datetime.now() - timedelta(days=7)
                
                for entry in feed.entries:
                    try:
                        # Parse entry date
                        entry_date = datetime(*entry.published_parsed[:6])
                        
                        if entry_date >= one_week_ago:
                            all_entries.append({
                                'title': entry.title,
                                'summary': entry.summary if hasattr(entry, 'summary') else '',
                                'link': entry.link,
                                'published': entry_date,
                                'source': feed_url
                            })
                    except:
                        # Skip entries with parsing issues
                        continue
                        
            except Exception as e:
                logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
                continue
        
        return sorted(all_entries, key=lambda x: x['published'], reverse=True)
    
    async def analyze_content_with_ai(self, content: str, content_type: str, 
                                    previous_content: str = None) -> Dict:
        """Analyze content using AI to detect changes and extract insights"""
        
        if content_type == "changelog":
            prompt = f"""
            Analyze this changelog/release notes content and identify:
            1. New features announced
            2. Product updates or improvements
            3. Pricing changes mentioned
            4. Deprecated features
            5. Key technical updates
            
            Content: {content}
            
            Provide a structured summary with clear categories.
            """
        elif content_type == "pricing":
            prompt = f"""
            Analyze this pricing page content and identify:
            1. Current pricing tiers and costs
            2. Any pricing changes or updates
            3. New plans or features
            4. Special offers or promotions
            5. Comparison with competitors mentioned
            
            Content: {content}
            
            Focus on extracting specific pricing information and any changes.
            """
        elif content_type == "blog":
            prompt = f"""
            Analyze this blog content and identify:
            1. Product announcements
            2. Company updates or news
            3. New features or capabilities discussed
            4. Strategic direction or messaging changes
            5. Customer success stories or case studies
            
            Content: {content}
            
            Summarize the key business and product insights.
            """
        else:  # website, social, app_store
            prompt = f"""
            Analyze this {content_type} content and identify:
            1. Key messaging and positioning
            2. New features or products mentioned
            3. Pricing information
            4. Company updates or announcements
            5. Competitive positioning
            
            Content: {content}
            
            Provide insights on business strategy and product updates.
            """
        
        if previous_content:
            prompt += f"\n\nPrevious content for comparison: {previous_content}\n\nHighlight what has changed between the previous and current content."
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.get('ai_model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are a competitive intelligence analyst. Provide clear, actionable insights about competitor activities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            ai_summary = response.choices[0].message.content
            
            # Extract detected changes
            changes = []
            if previous_content and previous_content != content:
                changes.append("Content updated since last monitoring")
                
                # Use AI to identify specific changes
                change_prompt = f"""
                Compare these two versions and list specific changes:
                
                Previous: {previous_content[:1000]}
                Current: {content[:1000]}
                
                List only the specific changes found.
                """
                
                change_response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": change_prompt}],
                    temperature=0.1
                )
                
                changes.append(change_response.choices[0].message.content)
            
            return {
                "ai_summary": ai_summary,
                "detected_changes": changes
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "ai_summary": "AI analysis failed",
                "detected_changes": []
            }
    
    async def monitor_target(self, target: CompetitorTarget) -> List[MonitoringResult]:
        """Monitor a single competitor target across all their channels"""
        results = []
        
        # Monitor main website
        logger.info(f"Monitoring {target.name} website: {target.website_url}")
        website_content = await self.scrape_website_content(target.website_url)
        if website_content:
            content_hash = hash(website_content)
            previous_data = self.historical_data.get(f"{target.name}_website", {})
            previous_content = previous_data.get('content', '')
            
            ai_analysis = await self.analyze_content_with_ai(
                website_content, "website", previous_content
            )
            
            result = MonitoringResult(
                timestamp=datetime.now(),
                target_name=target.name,
                content_type="website",
                url=target.website_url,
                content_hash=str(content_hash),
                raw_content=website_content,
                ai_summary=ai_analysis['ai_summary'],
                detected_changes=ai_analysis['detected_changes'],
                metadata={}
            )
            results.append(result)
            
            # Update historical data
            self.historical_data[f"{target.name}_website"] = {
                'content': website_content,
                'hash': str(content_hash),
                'last_updated': datetime.now().isoformat()
            }
        
        # Monitor changelog if available
        if target.changelog_url:
            logger.info(f"Monitoring {target.name} changelog: {target.changelog_url}")
            changelog_content = await self.scrape_website_content(target.changelog_url)
            if changelog_content:
                content_hash = hash(changelog_content)
                previous_data = self.historical_data.get(f"{target.name}_changelog", {})
                previous_content = previous_data.get('content', '')
                
                ai_analysis = await self.analyze_content_with_ai(
                    changelog_content, "changelog", previous_content
                )
                
                result = MonitoringResult(
                    timestamp=datetime.now(),
                    target_name=target.name,
                    content_type="changelog",
                    url=target.changelog_url,
                    content_hash=str(content_hash),
                    raw_content=changelog_content,
                    ai_summary=ai_analysis['ai_summary'],
                    detected_changes=ai_analysis['detected_changes'],
                    metadata={}
                )
                results.append(result)
                
                self.historical_data[f"{target.name}_changelog"] = {
                    'content': changelog_content,
                    'hash': str(content_hash),
                    'last_updated': datetime.now().isoformat()
                }
        
        # Monitor pricing if available
        if target.pricing_url:
            logger.info(f"Monitoring {target.name} pricing: {target.pricing_url}")
            pricing_content = await self.scrape_website_content(target.pricing_url)
            if pricing_content:
                content_hash = hash(pricing_content)
                previous_data = self.historical_data.get(f"{target.name}_pricing", {})
                previous_content = previous_data.get('content', '')
                
                ai_analysis = await self.analyze_content_with_ai(
                    pricing_content, "pricing", previous_content
                )
                
                result = MonitoringResult(
                    timestamp=datetime.now(),
                    target_name=target.name,
                    content_type="pricing",
                    url=target.pricing_url,
                    content_hash=str(content_hash),
                    raw_content=pricing_content,
                    ai_summary=ai_analysis['ai_summary'],
                    detected_changes=ai_analysis['detected_changes'],
                    metadata={}
                )
                results.append(result)
                
                self.historical_data[f"{target.name}_pricing"] = {
                    'content': pricing_content,
                    'hash': str(content_hash),
                    'last_updated': datetime.now().isoformat()
                }
        
        # Monitor blog/RSS feeds if available
        if target.rss_feeds:
            logger.info(f"Monitoring {target.name} RSS feeds")
            rss_entries = await self.scrape_rss_feeds(target.rss_feeds)
            if rss_entries:
                rss_content = "\n\n".join([
                    f"Title: {entry['title']}\nSummary: {entry['summary']}\nLink: {entry['link']}"
                    for entry in rss_entries[:5]  # Limit to 5 most recent
                ])
                
                ai_analysis = await self.analyze_content_with_ai(rss_content, "blog")
                
                result = MonitoringResult(
                    timestamp=datetime.now(),
                    target_name=target.name,
                    content_type="blog",
                    url=str(target.rss_feeds),
                    content_hash=str(hash(rss_content)),
                    raw_content=rss_content,
                    ai_summary=ai_analysis['ai_summary'],
                    detected_changes=ai_analysis['detected_changes'],
                    metadata={'entry_count': len(rss_entries)}
                )
                results.append(result)
        
        return results
    
    async def run_monitoring_cycle(self) -> List[MonitoringResult]:
        """Run a complete monitoring cycle for all targets"""
        logger.info("Starting monitoring cycle")
        all_results = []
        
        for target in self.targets:
            try:
                target_results = await self.monitor_target(target)
                all_results.extend(target_results)
            except Exception as e:
                logger.error(f"Error monitoring {target.name}: {str(e)}")
                continue
        
        # Save historical data
        self._save_historical_data()
        
        logger.info(f"Monitoring cycle completed. {len(all_results)} results collected.")
        return all_results
    
    def generate_weekly_summary(self, results: List[MonitoringResult]) -> str:
        """Generate a comprehensive weekly summary"""
        if not results:
            return "No monitoring results available for this week."
        
        summary_prompt = f"""
        Generate a comprehensive weekly competitive intelligence summary based on the following monitoring results:

        {chr(10).join([f"Company: {r.target_name}, Type: {r.content_type}, Changes: {len(r.detected_changes)}, Summary: {r.ai_summary[:200]}..." for r in results])}

        Structure the summary with:
        1. Executive Summary - key highlights across all competitors
        2. New Features & Product Updates by company
        3. Pricing Changes detected
        4. Strategic Messaging Shifts
        5. Competitive Implications and Recommendations

        Make it actionable for business decision makers.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.get('ai_model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are a senior competitive intelligence analyst creating executive summaries."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {str(e)}")
            
            # Fallback to basic summary
            summary = "# Weekly Competitive Intelligence Summary\n\n"
            
            companies = {}
            for result in results:
                if result.target_name not in companies:
                    companies[result.target_name] = []
                companies[result.target_name].append(result)
            
            for company, company_results in companies.items():
                summary += f"## {company}\n"
                for result in company_results:
                    summary += f"- **{result.content_type.title()}**: "
                    if result.detected_changes:
                        summary += f"{len(result.detected_changes)} changes detected\n"
                    else:
                        summary += "No changes detected\n"
                    summary += f"  {result.ai_summary[:150]}...\n\n"
            
            return summary
    
    async def send_to_slack(self, summary: str, results: List[MonitoringResult]):
        """Send summary to Slack"""
        if not self.slack_client:
            logger.warning("Slack client not configured")
            return
        
        try:
            channel = os.getenv('SLACK_CHANNEL', '#competitive-intelligence')
            
            # Create Slack blocks for better formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🕵️ Weekly Competitive Intelligence Report"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary[:3000]  # Slack has message limits
                    }
                }
            ]
            
            # Add quick stats
            companies_monitored = len(set(r.target_name for r in results))
            total_changes = sum(len(r.detected_changes) for r in results)
            
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📊 Monitored {companies_monitored} companies | {total_changes} changes detected | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                ]
            })
            
            response = self.slack_client.chat_postMessage(
                channel=channel,
                blocks=blocks
            )
            
            logger.info(f"Summary sent to Slack channel {channel}")
            
        except Exception as e:
            logger.error(f"Failed to send to Slack: {str(e)}")
    
    async def send_to_notion(self, summary: str, results: List[MonitoringResult]):
        """Send summary to Notion"""
        if not self.notion_client:
            logger.warning("Notion client not configured")
            return
        
        try:
            database_id = os.getenv('NOTION_DATABASE_ID')
            if not database_id:
                logger.error("NOTION_DATABASE_ID not configured")
                return
            
            # Create page in Notion database
            page_data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": f"Competitive Intelligence Report - {datetime.now().strftime('%Y-%m-%d')}"
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    },
                    "Companies Monitored": {
                        "number": len(set(r.target_name for r in results))
                    },
                    "Changes Detected": {
                        "number": sum(len(r.detected_changes) for r in results)
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": summary
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            response = self.notion_client.pages.create(**page_data)
            logger.info(f"Summary sent to Notion database {database_id}")
            
        except Exception as e:
            logger.error(f"Failed to send to Notion: {str(e)}")
    
    async def run_weekly_report(self):
        """Run the weekly monitoring and generate report"""
        logger.info("Starting weekly competitive intelligence report")
        
        # Run monitoring cycle
        results = await self.run_monitoring_cycle()
        
        if not results:
            logger.warning("No results collected, skipping report generation")
            return
        
        # Generate summary
        summary = self.generate_weekly_summary(results)
        
        # Send notifications
        notification_channels = self.config.get('notification_channels', ['slack', 'notion'])
        
        if 'slack' in notification_channels:
            await self.send_to_slack(summary, results)
        
        if 'notion' in notification_channels:
            await self.send_to_notion(summary, results)
        
        # Save report locally
        report_filename = f"reports/competitive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        os.makedirs('reports', exist_ok=True)
        
        with open(report_filename, 'w') as f:
            f.write(f"# Competitive Intelligence Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(summary)
            f.write(f"\n\n## Detailed Results\n\n")
            
            for result in results:
                f.write(f"### {result.target_name} - {result.content_type.title()}\n")
                f.write(f"URL: {result.url}\n")
                f.write(f"Timestamp: {result.timestamp}\n")
                f.write(f"Changes: {len(result.detected_changes)}\n")
                f.write(f"Summary: {result.ai_summary}\n\n")
        
        logger.info(f"Report saved to {report_filename}")

def setup_monitoring_schedule(monitor: AICompetitorMonitor):
    """Setup scheduled monitoring"""
    frequency = monitor.config.get('monitoring_frequency', 'weekly')
    
    if frequency == 'daily':
        schedule.every().day.at("09:00").do(lambda: asyncio.run(monitor.run_weekly_report()))
    elif frequency == 'weekly':
        schedule.every().monday.at("09:00").do(lambda: asyncio.run(monitor.run_weekly_report()))
    elif frequency == 'monthly':
        schedule.every().month.do(lambda: asyncio.run(monitor.run_weekly_report()))
    
    logger.info(f"Scheduled monitoring frequency: {frequency}")

async def main():
    """Main function to run the competitive intelligence monitor"""
    monitor = AICompetitorMonitor()
    
    # Setup scheduled monitoring
    setup_monitoring_schedule(monitor)
    
    # Run initial report
    logger.info("Running initial competitive intelligence report...")
    await monitor.run_weekly_report()
    
    # Keep the scheduler running
    logger.info("Starting scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(main())