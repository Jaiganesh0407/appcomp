# AI Competitor Monitor 🕵️

An intelligent AI agent that monitors competitor websites, changelogs, app updates, and social announcements, delivering comprehensive weekly summaries to Slack, Notion, or other platforms.

## Features 🚀

- **Multi-Channel Monitoring**: Track websites, changelogs, pricing pages, blogs, RSS feeds, and social media
- **AI-Powered Analysis**: Uses GPT-4 to analyze content and detect meaningful changes
- **Change Detection**: Automatically identifies new features, pricing updates, and strategic shifts
- **Smart Scheduling**: Configurable monitoring frequency (daily, weekly, monthly)
- **Multiple Integrations**: Send reports to Slack, Notion, email, or custom webhooks
- **Historical Tracking**: Maintains history to identify trends and changes over time
- **Easy Configuration**: JSON-based configuration for targets and settings
- **CLI Management**: Command-line tools for easy setup and management

## Architecture 🏗️

```
AI Competitor Monitor
├── Web Scraping Layer (requests + Selenium)
├── AI Analysis Engine (OpenAI GPT-4)
├── Change Detection System
├── Data Storage (JSON + optional database)
├── Notification System (Slack, Notion, Email)
└── Scheduler (automated weekly reports)
```

## Quick Start 🚀

### 1. Installation

```bash
# Clone or download the project
git clone <your-repo-url>
cd ai-competitor-monitor

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Configuration

Edit `.env` with your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional integrations
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SLACK_CHANNEL=#competitive-intelligence
NOTION_TOKEN=secret_your_notion_integration_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

### 3. Set Up Monitoring Targets

The system comes with example targets (Notion, Airtable, Monday.com, etc.). You can:

```bash
# View current targets
python cli.py list-targets

# Add a new target
python cli.py add-target

# Remove a target
python cli.py remove-target
```

### 4. Test Configuration

```bash
# Test your setup
python cli.py test-config
```

### 5. Run Monitoring

```bash
# Run once
python cli.py run

# Start scheduled monitoring
python competitor_monitor.py
```

## Configuration Files 📝

### `targets.json` - Monitoring Targets

```json
[
  {
    "name": "Competitor Name",
    "website_url": "https://competitor.com",
    "changelog_url": "https://competitor.com/changelog",
    "pricing_url": "https://competitor.com/pricing", 
    "blog_url": "https://competitor.com/blog",
    "social_urls": ["https://twitter.com/competitor"],
    "app_store_urls": {
      "ios": "https://apps.apple.com/app/competitor-app/id123456789",
      "android": "https://play.google.com/store/apps/details?id=com.competitor.app"
    },
    "rss_feeds": ["https://competitor.com/blog/rss"]
  }
]
```

### `config.json` - System Settings

```json
{
  "monitoring_frequency": "weekly",
  "ai_model": "gpt-4",
  "max_content_length": 5000,
  "timeout": 30,
  "enable_selenium": true,
  "notification_channels": ["slack", "notion"]
}
```

## Integrations 🔗

### Slack Integration

1. Create a Slack app at https://api.slack.com/apps
2. Add Bot Token Scopes: `chat:write`, `chat:write.public`
3. Install app to your workspace
4. Copy Bot User OAuth Token to `.env`

### Notion Integration

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Create a database for reports
3. Share database with your integration
4. Copy integration token and database ID to `.env`

### Email Integration

Configure SMTP settings in `.env`:

```env
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=team@company.com
```

## CLI Commands 💻

```bash
# Target management
python cli.py add-target          # Add new competitor
python cli.py list-targets        # List all targets
python cli.py remove-target       # Remove a target

# Monitoring
python cli.py run                 # Run monitoring once
python cli.py test-config         # Test configuration
python cli.py status              # Show system status
```

## Monitoring Capabilities 📊

### What It Monitors

- **Website Changes**: Homepage updates, new features, messaging shifts
- **Changelogs**: New releases, feature announcements, deprecations
- **Pricing**: Price changes, new plans, promotional offers
- **Blog Posts**: Product announcements, company news, thought leadership
- **Social Media**: Twitter announcements, product updates
- **App Stores**: New app versions, feature updates, user reviews trends
- **RSS Feeds**: Latest blog posts and announcements

### AI Analysis Features

- **Change Detection**: Identifies specific changes between monitoring cycles
- **Feature Extraction**: Highlights new features and product updates
- **Pricing Analysis**: Detects pricing changes and new plans
- **Competitive Intelligence**: Provides strategic insights and recommendations
- **Trend Analysis**: Identifies patterns across multiple monitoring cycles

## Reports 📈

### Weekly Summary Report

The AI generates comprehensive weekly reports including:

1. **Executive Summary** - Key highlights across all competitors
2. **New Features & Updates** - Product changes by company
3. **Pricing Changes** - Any pricing updates detected
4. **Strategic Messaging** - Changes in positioning or messaging
5. **Competitive Implications** - Actionable insights and recommendations

### Report Formats

- **Slack**: Rich formatted messages with quick stats
- **Notion**: Database entries with structured data
- **Email**: HTML formatted reports
- **Local Files**: Markdown reports saved to `reports/` directory

## Scheduling 📅

### Automated Monitoring

```bash
# Start the scheduler (runs continuously)
python competitor_monitor.py
```

### Frequency Options

- `daily`: Every day at 9:00 AM
- `weekly`: Every Monday at 9:00 AM  
- `monthly`: First Monday of each month

Configure in `config.json`:

```json
{
  "monitoring_frequency": "weekly"
}
```

### Using Cron (Alternative)

```bash
# Add to crontab for weekly Monday 9 AM runs
0 9 * * 1 /path/to/python /path/to/cli.py run
```

## Data Storage 💾

### Local Storage

- `historical_data.json`: Stores content hashes and change history
- `reports/`: Generated reports in Markdown format
- `competitor_monitor.log`: Application logs

### Database Integration (Optional)

Configure PostgreSQL in `.env` for production use:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/competitor_monitor
```

## Advanced Features ⚙️

### Selenium Web Scraping

For JavaScript-heavy sites, enable Selenium:

```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser

# Or download ChromeDriver manually
```

### Custom Webhooks

Send data to custom endpoints:

```env
WEBHOOK_URL=https://your-api.com/competitor-updates
```

### Content Filtering

Configure keywords in `config.json`:

```json
{
  "changelog_keywords": ["release", "update", "new", "feature"],
  "pricing_keywords": ["price", "plan", "subscription", "cost"]
}
```

## Monitoring Best Practices 📋

### Target Selection

- Include direct competitors and market leaders
- Monitor different types of content (pricing, features, messaging)
- Add RSS feeds for timely updates
- Include mobile app stores for mobile competitors

### Configuration Tips

- Start with weekly monitoring to avoid rate limiting
- Use Selenium for JavaScript-heavy sites
- Set appropriate timeouts for slow sites
- Monitor 5-10 competitors initially

### API Management

- Use OpenAI API responsibly to manage costs
- Consider GPT-3.5-turbo for cost optimization
- Implement rate limiting for high-frequency monitoring
- Monitor API usage and costs regularly

## Troubleshooting 🔧

### Common Issues

1. **Scraping Failures**
   - Check if sites block automated requests
   - Enable Selenium for JavaScript sites
   - Verify target URLs are accessible

2. **API Errors**
   - Verify API keys in `.env`
   - Check API quotas and billing
   - Test with `python cli.py test-config`

3. **Integration Issues**
   - Verify Slack bot permissions
   - Check Notion database sharing settings
   - Test notification channels individually

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check logs
tail -f competitor_monitor.log

# Test individual components
python cli.py test-config
```

### Rate Limiting

If you encounter rate limiting:

- Increase delays between requests
- Use different user agents
- Enable proxy rotation (custom implementation)
- Reduce monitoring frequency

## Cost Considerations 💰

### OpenAI API Costs

- GPT-4: ~$0.03 per 1K tokens
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- Estimated weekly cost: $5-20 for 10 competitors

### Optimization Tips

- Use GPT-3.5-turbo for basic analysis
- Limit content length (configured in settings)
- Only run AI analysis on detected changes
- Cache results to avoid duplicate analysis

## Security & Privacy 🔒

### Data Handling

- All scraped content stored locally by default
- No data sent to third parties except configured integrations
- API keys stored in environment variables
- Historical data can be encrypted (custom implementation)

### Best Practices

- Rotate API keys regularly
- Use read-only database users
- Implement access controls for sensitive data
- Monitor for compliance with competitor terms of service

## Contributing 🤝

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Integration Examples

- Add new notification channels
- Implement database backends
- Create custom analysis modules
- Add new data sources

## License 📜

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For questions, issues, or feature requests:

1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include logs and configuration (without sensitive data)

---

**Built with ❤️ for competitive intelligence teams**