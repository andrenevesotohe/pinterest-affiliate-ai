# Pinterest Affiliate AI

Automated Pinterest posting with AI-generated beauty content.

## Overview

This project automates the creation and posting of beauty-related content to Pinterest, leveraging AI to generate engaging posts and manage affiliate links.

## Features

- AI-powered content generation
- Automated Pinterest posting
- Amazon affiliate link integration
- Trend analysis and optimization
- Safety checks and rate limiting
- Scheduled daily execution

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/pinterest-affiliate-ai.git
cd pinterest-affiliate-ai
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file with:
```
OPENAI_API_KEY="your-key-here"
PINTEREST_ACCESS_TOKEN="your-token"
AMAZON_ASSOCIATE_TAG="your-tag"
PINTEREST_BOARD_ID="your-board-id"
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── pytest.yml
│       └── schedule.yml
├── .venv/
├── tests/
├── modules/
│   ├── __init__.py
│   ├── trends.py
│   ├── poster.py
│   └── content_generator.py
├── config/
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── main.py
├── scheduler.py
├── scheduler.json
└── requirements.txt
```

## Scheduled Execution

The project includes a scheduler that runs the Pinterest posting process daily at 9AM UTC.

### Using the Scheduler

1. Start the scheduler:
```bash
python scheduler.py
```

2. The scheduler will run in the background and execute the daily posting task at the scheduled time.

3. You can modify the schedule in `scheduler.json`:
```json
{
  "tasks": [
    {
      "name": "pinterest_affiliate_daily_post",
      "command": "python main.py",
      "schedule": "0 9 * * *",  # Daily at 9AM UTC
      "timezone": "UTC",
      "enabled": true
    }
  ]
}
```

### Running as a Service

For production use, you can set up the scheduler as a system service:

#### Linux (systemd)
Create a file at `/etc/systemd/system/pinterest-affiliate.service`:
```
[Unit]
Description=Pinterest Affiliate AI Scheduler
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/pinterest-affiliate
ExecStart=/path/to/pinterest-affiliate/.venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:
```bash
sudo systemctl enable pinterest-affiliate
sudo systemctl start pinterest-affiliate
```

## Development

- Create feature branches from `dev`
- Run tests before committing: `python -m pytest tests/ -v`
- Follow the protected branch workflow

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
