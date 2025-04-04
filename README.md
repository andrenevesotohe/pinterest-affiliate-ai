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
├── config/
├── .env
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Development

- Create feature branches from `dev`
- Run tests before committing: `python -m pytest tests/ -v`
- Follow the protected branch workflow

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 