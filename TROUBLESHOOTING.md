# Pinterest Affiliate AI Troubleshooting Guide

This guide provides step-by-step instructions for troubleshooting common issues with the Pinterest Affiliate AI.

## Environment Setup

### 1. Environment Variables

The application requires several environment variables to be set in the `.env` file:

```ini
# API Keys
OPENAI_API_KEY=your_openai_api_key
PINTEREST_TOKEN=your_pinterest_token  # Must start with "pina_"
PINTEREST_BOARD_ID=your_pinterest_board_id
AMAZON_ASSOCIATE_TAG=your_amazon_associate_tag

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=your_notification_email@example.com

# Alert Email Configuration
ALERT_EMAIL_FROM=your_email@gmail.com
ALERT_EMAIL_TO=your_notification_email@example.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

#### Getting Your API Keys

1. **Pinterest Token**
   - Go to [Pinterest Developer Portal](https://developers.pinterest.com/apps/)
   - Create a new app or select an existing one
   - Request the following OAuth scopes:
     - `pins:write` - Required for posting pins
     - `boards:read` - Required for accessing board information
   - Generate an access token
   - The token should start with "pina_" and be much longer than a simple number

2. **OpenAI API Key**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key (starts with "sk-")

3. **Amazon Associate Tag**
   - Go to [Amazon Associates](https://affiliate-program.amazon.com/)
   - Sign in to your account
   - Find your Associate Tag (format: `username-20`)

### 2. Environment Validation

To validate that all required environment variables are present:

```bash
python scripts/check_env.py
```

To also test API connectivity:

```bash
python scripts/check_env.py --test-connectivity
```

### 3. API Testing

To test connectivity to external APIs:

```bash
# Test all APIs
python scripts/test_api.py

# Test specific APIs
python scripts/test_api.py --pinterest
python scripts/test_api.py --openai
python scripts/test_api.py --amazon
```

## Test Mode

The Pinterest Affiliate AI includes a test mode that allows you to run the system without making actual API calls or charges.

### Running in Test Mode

To run the system in test mode:

```bash
# Run with test mode and limit to 2 posts
python main.py --test-mode --limit 2
```

Or use the test run script:

```bash
python scripts/test_run.py
```

### Test Mode Features

When running in test mode:

1. **No API Charges**: The system uses mock data instead of making real API calls to OpenAI/DALL-E
2. **Empty Fallback Queue**: The fallback queue is cleared at the start and verified empty at the end
3. **Logging**: All actions are logged to the logs directory
4. **Mock Data**: Uses predefined mock trends and content instead of real data

### Test Mode Verification

The test run script verifies:

1. ✅ logs/ directory created with pinterest.log and errors.log
2. ✅ fallback_queue.json remains empty
3. ✅ No charges to your OpenAI/DALL-E accounts (test mode doesn't use real credits)

## Working with Pinterest Boards

### Getting Board Information

You can get information about your Pinterest boards using the `get_board.py` script:

```bash
# Get information about the default board (from .env)
python scripts/get_board.py

# Get information about a specific board
python scripts/get_board.py --board-id "username/board-name/"

# Get board sections
python scripts/get_board.py --sections

# Output in JSON format
python scripts/get_board.py --json
```

### Test Board Reading

To test reading board information with sample data:

```bash
python scripts/test_get_board.py
```

This will:
- Get board details (name, description, privacy, etc.)
- Get board sections
- Save the information to `board_info.json`

### Board Parameters

When working with boards, note:
- Board ID format: `username/board-name/`
- Board sections are optional
- Privacy can be "public" or "secret"
- Board names can contain spaces and special characters
- Board descriptions are optional

### Common Board Issues

1. **401 Unauthorized**
   - Check your Pinterest token
   - Ensure it has the `boards:read` scope
   - Try refreshing the token

2. **404 Not Found**
   - Verify the board ID format
   - Check if the board exists
   - Ensure you have access to the board

3. **403 Forbidden**
   - Check if you have permission to access the board
   - Verify the board's privacy settings
   - Ensure your app has the correct scopes

## Creating Pinterest Pins

### Manual Pin Creation

You can create individual pins using the `create_pin.py` script:

```bash
python scripts/create_pin.py \
  --title "Your Pin Title" \
  --description "Your pin description with #hashtags" \
  --link "https://www.amazon.com/dp/PRODUCT_ID?tag=your-tag" \
  --image-url "https://example.com/image.jpg" \
  --alt-text "Image description for accessibility"
```

### Test Pin Creation

To create a test pin with sample data:

```bash
python scripts/test_create_pin.py
```

This will create a test pin using:
- A sample beauty product title and description
- Your Amazon affiliate tag
- A sample image from Pexels
- Appropriate alt text

### Pin Creation Parameters

When creating pins, note these limitations:
- Title: Max 100 characters
- Description: Max 500 characters
- Alt text: Max 500 characters
- Image URL must be publicly accessible
- Link must be a valid URL
- Board ID must be in the format `username/board-name/`

### Common Pin Creation Issues

1. **401 Unauthorized**
   - Check your Pinterest token
   - Ensure it has the `pins:write` scope
   - Try refreshing the token

2. **400 Bad Request**
   - Check image URL accessibility
   - Verify board ID format
   - Ensure title/description lengths are within limits

3. **429 Too Many Requests**
   - You've hit the Pinterest API rate limit
   - Wait a few minutes before retrying
   - Consider implementing rate limiting in your code

## Common Issues

### 1. Pinterest API Authentication (401 Error)

If you're experiencing 401 errors when posting to Pinterest, it's likely that your API token has expired or is invalid.

#### Solution:

1. Verify your token:
   ```bash
   python scripts/verify_pinterest_token.py
   ```

2. If the token is invalid, refresh it:
   ```bash
   python scripts/refresh_token.py
   ```

3. Update your `.env` file with the new token if needed.

### 2. Fallback Queue Issues

If posts are being added to the fallback queue instead of being posted directly, it could be due to various issues.

#### Solution:

1. Clear the fallback queue:
   ```bash
   python scripts/clear_queue.py
   ```

2. Process the fallback queue:
   ```bash
   python scripts/process_queue.py
   ```

### 3. Budget Tracking Issues

If you're experiencing issues with the budget tracker, you can reset it.

#### Solution:

1. Reset the budget tracker:
   ```bash
   python scripts/reset_budget.py
   ```

### 4. Environment Verification

To verify that your environment is properly configured:

```bash
python scripts/verify_environment.py
```

This will check:
- Required environment variables
- Required Python packages
- Run tests
- Check affiliate links

## Testing

### Dry Run Test

To run a dry run test (no actual posts will be made):

```bash
python scripts/dry_run.py --limit 2 --budget 0.08
```

This will:
- Fetch beauty trends
- Generate content
- Simulate posting to Pinterest
- Not actually post to Pinterest

### Live Test

To run a live test (will actually post to Pinterest):

```bash
python scripts/live_test.py --limit 2 --budget 0.08
```

This will:
- Fetch beauty trends
- Generate content
- Actually post to Pinterest

### Test Post

To test a single post to Pinterest:

```bash
python scripts/test_post.py --live
```

This will:
- Post a test image to Pinterest
- Verify that the Pinterest API is working correctly

## All-in-One Troubleshooting

To run all troubleshooting steps at once:

```bash
python scripts/troubleshoot.py --limit 2 --budget 0.08
```

This will:
1. Verify Pinterest token
2. Refresh token if needed
3. Clear fallback queue
4. Reset budget tracker
5. Verify environment
6. Run dry run test

To also run a live test:

```bash
python scripts/troubleshoot.py --limit 2 --budget 0.08 --live
```

## Automation Scripts

The following scripts are scheduled to run automatically to prevent issues:

### 1. Token Refresh

The Pinterest API token is automatically refreshed on the 1st of every month:

```bash
python scripts/refresh_token.py
```

To test the token refresh without actually refreshing:

```bash
python scripts/refresh_token.py --test
```

### 2. Queue Processing

Failed posts are automatically retried every 4 hours:

```bash
python scripts/process_queue.py
```

To test queue processing without actually posting:

```bash
python scripts/process_queue.py --dry-run
```

### 3. Budget Alerts

Budget alerts are sent daily at 6PM UTC when budgets are running low:

```bash
python scripts/budget_alerts.py
```

To test budget alerts without actually sending emails:

```bash
python scripts/budget_alerts.py --test
```

## Monitoring

To monitor the logs:

```bash
tail -f logs/pinterest.log -n 20
```

To monitor error logs:

```bash
tail -f logs/errors.log -n 20
```

To monitor specific automation logs:

```bash
tail -f token_refresh.log -n 20  # Token refresh logs
tail -f queue_processor.log -n 20  # Queue processing logs
tail -f budget_alerts.log -n 20  # Budget alert logs
```

## Expected Outcomes

| Component | Success Criteria |
|-----------|------------------|
| API Auth | 200 responses |
| Fallback Queue | 0 items after test |
| Budget Tracking | $0.00 remaining after 2 posts |
| Pinterest Board | 2 new posts visible |

## Time Estimate

| Task | Duration |
|------|----------|
| Token Refresh | 5 mins |
| Queue Clearance | 3 mins |
| Budget Reset | 2 mins |
| Verification | 5 mins |
| **Total** | **15 mins** | 