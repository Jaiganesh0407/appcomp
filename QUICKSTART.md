# AI Competitor Monitor - Quick Start Guide 🚀

Get your AI competitor monitoring system up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Git (optional)
- OpenAI API key (required)
- Slack/Notion integration tokens (optional)

## 🔧 Step 1: Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔑 Step 2: Configure API Keys

Copy the environment template and add your API keys:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Required:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

**Optional (for notifications):**
- `SLACK_BOT_TOKEN` - Create app at https://api.slack.com/apps
- `NOTION_TOKEN` - Create integration at https://www.notion.so/my-integrations

## 🎯 Step 3: Review Targets

The system comes with example competitors (Notion, Airtable, Monday.com, etc.):

```bash
# View current targets
python cli.py list-targets

# Add your own competitors
python cli.py add-target
```

## ✅ Step 4: Test Configuration

```bash
# Test your setup
python cli.py test-config
```

## 🚀 Step 5: Run Your First Monitoring

```bash
# Run once to test
python cli.py run

# Check the generated report
ls reports/
```

## ⏰ Step 6: Start Automated Monitoring

```bash
# Start the scheduler (runs weekly on Mondays at 9 AM)
python competitor_monitor.py
```

## 📊 What You Get

- **AI-Powered Analysis**: GPT-4 analyzes competitor changes
- **Multiple Channels**: Websites, changelogs, pricing, blogs, social media
- **Smart Notifications**: Slack and Notion integration
- **Historical Tracking**: Compare changes over time
- **Executive Summaries**: Business-ready reports

## 🎛️ Customization

### Change Monitoring Frequency

Edit `config.json`:
```json
{
  "monitoring_frequency": "daily"  // or "weekly", "monthly"
}
```

### Add More Competitors

```bash
python cli.py add-target
```

### Configure Notifications

Update notification channels in `config.json`:
```json
{
  "notification_channels": ["slack", "notion"]
}
```

## 🐳 Docker Deployment (Optional)

```bash
# Build and run with Docker
docker-compose up -d
```

## 📁 Important Files

- `config.json` - System configuration
- `targets.json` - Competitor monitoring targets
- `.env` - API keys and secrets
- `reports/` - Generated monitoring reports
- `historical_data.json` - Change tracking data

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Errors**: Check your API keys in `.env`
3. **Selenium Issues**: Install Chrome: `sudo apt-get install chromium-browser`

### Test Everything

```bash
python test_system.py
```

### Get Help

```bash
python cli.py --help
```

## 💡 Pro Tips

1. **Start Small**: Begin with 3-5 competitors to test the system
2. **Weekly Monitoring**: Use weekly frequency initially to avoid rate limits
3. **Check Reports**: Review the `reports/` directory for generated summaries
4. **Monitor Logs**: Check `competitor_monitor.log` for system status
5. **Customize AI Model**: Edit `config.json` to use `gpt-3.5-turbo` for cost savings

## 🔄 What's Next?

1. Review your first generated report
2. Add more competitors relevant to your business
3. Set up Slack/Notion notifications
4. Schedule the system to run automatically
5. Analyze trends and competitive insights

---

**Need more help?** Check the full README.md for detailed documentation!

## 📈 Example Output

Your monitoring reports will include:

- **Executive Summary**: Key highlights across all competitors
- **New Features**: Product updates and announcements
- **Pricing Changes**: Any pricing updates detected
- **Strategic Messaging**: Changes in positioning
- **Competitive Implications**: Actionable insights and recommendations

Ready to gain competitive intelligence advantage? Let's get started! 🎯