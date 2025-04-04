# Pinterest Affiliate AI

An automated system for generating and posting beauty content to Pinterest with affiliate links.

## Features

- **Trend Analysis**: Automatically identifies beauty trends on Pinterest
- **Content Generation**: Creates high-quality images and captions using DALL-E and GPT-3.5
- **Affiliate Integration**: Adds Amazon affiliate links to posts
- **Budget Management**: Tracks and limits DALL-E API usage
- **Resilient Posting**: Handles API failures with retry logic and fallback queue
- **Maintenance Tools**: Includes scripts for log rotation, budget reset, and diagnostics

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pinterest-affiliate.git
   cd pinterest-affiliate
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and fill in your API keys:
   ```
   cp .env.example .env
   ```

## Configuration

Edit the `.env` file with your API keys and settings:

```
OPENAI_API_KEY=your_openai_api_key
PINTEREST_TOKEN=your_pinterest_token
PINTEREST_BOARD_ID=your_pinterest_board_id
AMAZON_ASSOCIATE_TAG=your_amazon_associate_tag
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=your_notification_email
```

## Usage

### Daily Posting

Run the system to automatically post content:

```
python main.py
```

### Test Mode

Run in test mode without actually posting:

```
python main.py --test-mode
```

### Dry Run

Run without posting to Pinterest:

```
python main.py --dry-run
```

### Limited Posts

Limit the number of posts:

```
python main.py --limit 3
```

### Budget Control

Set a maximum DALL-E budget:

```
python main.py --budget 0.12
```

## Maintenance

### Daily Maintenance

Run all daily maintenance tasks:

```
python scripts/maintenance.py --daily
```

### Log Rotation

Rotate log files:

```
python scripts/maintenance.py --rotate-logs
```

### Budget Reset

Reset the DALL-E budget:

```
python scripts/maintenance.py --reset-budget
```

### Process Fallback Queue

Process the fallback queue:

```
python scripts/maintenance.py --process-queue
```

### Check Affiliate Links

Check affiliate links for validity:

```
python scripts/maintenance.py --check-links
```

## Diagnostics

Run diagnostics on the last execution:

```
python scripts/diagnose.py --last-run
```

## Testing

Run the test suite:

```
python -m pytest tests/ -v
```

Run with coverage:

```
python -m pytest tests/ -v --cov=modules --cov-report=html
```

## Scheduling

The system includes a scheduler for automated tasks:

```
python scheduler.py
```

Tasks are configured in `scheduler.json`:

```json
{
  "tasks": [
    {
      "name": "pinterest_affiliate_daily_post",
      "command": "python main.py",
      "schedule": "0 9 * * *",
      "timezone": "UTC",
      "enabled": true,
      "description": "Run Pinterest Affiliate Automation AI daily at 9AM UTC"
    },
    {
      "name": "validate_affiliate_links",
      "command": "python scripts/check_affiliate_links.py --notify",
      "schedule": "0 8 * * *",
      "timezone": "UTC",
      "enabled": true,
      "description": "Validate affiliate links daily at 8AM UTC"
    },
    {
      "name": "process_fallback_queue",
      "command": "python scripts/process_fallback.py",
      "schedule": "0 */4 * * *",
      "timezone": "UTC",
      "enabled": true,
      "description": "Process fallback queue every 4 hours"
    },
    {
      "name": "check_gpt_usage",
      "command": "python scripts/check_gpt_usage.py",
      "schedule": "0 0 * * *",
      "timezone": "UTC",
      "enabled": true,
      "description": "Check GPT usage daily at midnight UTC"
    }
  ]
}
```

## Project Structure

```
pinterest-affiliate/
├── modules/                  # Core modules
│   ├── budget_tracker.py     # DALL-E budget tracking
│   ├── content_generator.py  # Content generation
│   ├── dalle_generator.py    # DALL-E image generation
│   ├── poster.py             # Pinterest posting
│   ├── text_generator.py     # GPT-3.5 text generation
│   └── trends.py             # Trend analysis
├── scripts/                  # Utility scripts
│   ├── check_affiliate_links.py  # Affiliate link validation
│   ├── check_gpt_usage.py        # GPT usage tracking
│   ├── diagnose.py               # Diagnostics
│   ├── maintenance.py            # Maintenance tasks
│   ├── process_fallback.py       # Fallback queue processing
│   ├── run_tests.py              # Test runner
│   └── verify_environment.py     # Environment verification
├── tests/                    # Test suite
├── .env                      # Environment variables
├── .env.example              # Example environment file
├── main.py                   # Main script
├── README.md                 # Documentation
├── requirements.txt          # Dependencies
└── scheduler.json            # Scheduler configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
