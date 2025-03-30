# Snapp Login Telegram Bot

A Telegram bot that manages Snapp user accounts, allowing users to add accounts, view account details, and list all registered accounts with pagination.

## Features

- 📱 Add new Snapp accounts with phone number verification
- 🔍 View detailed account information
- 📋 List all registered accounts with pagination (20 accounts per page)
- 🔄 Automatic token expiration tracking
- 🔒 Secure storage of account credentials
- 👤 Store user's full name from Snapp

## Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/amir-wyvern/snapp-login.git
cd snapp-login
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```

5. Edit .env and add your configuration:
```env
# Bot Settings
BOT_TOKEN=your_bot_token_here

# Proxy Settings (if needed)
HTTP_PROXY=http://your-proxy-server:port
HTTPS_PROXY=http://your-proxy-server:port
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/snapp-login-bot.git
cd snapp-login-bot
```

2. Create and configure .env file as described above.

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

## Usage

1. Start a chat with your bot on Telegram

2. Available commands:
   - `/start` - Start the bot and show main menu
   - Click "➕ Add Account" to add a new Snapp account
   - Click "📱 Get Data" to view account details
   - Click "📋 List Accounts" to see all registered accounts

3. Adding a new account:
   - Click "➕ Add Account"
   - Enter phone number (10 digits, without +98 or 0)
   - Enter the OTP code received on your phone
   - Account will be saved automatically

4. Viewing account data:
   - Click "📱 Get Data"
   - Enter the phone number
   - View detailed account information

5. Listing accounts:
   - Click "📋 List Accounts"
   - View accounts in pages of 20
   - Use navigation buttons to move between pages
   - Click on any phone number to view its details

## Project Structure

```
snapp-login-bot/
├── bot.py           # Main bot implementation
├── models.py        # Database models
├── snapp_module.py  # Snapp API integration
├── requirements.txt # Python dependencies
├── Dockerfile      # Docker configuration
├── docker-compose.yml
└── .env            # Configuration file
```

## Database

The bot uses SQLite database (located in `data/snapp.db`) to store:
- Phone numbers
- Full names
- Access tokens
- Refresh tokens
- Login timestamps
- Token expiration times
- Account status

## Error Handling

The bot includes comprehensive error handling for:
- Invalid phone numbers
- Invalid OTP codes
- Expired tokens
- Network errors
- Database errors

## Deployment

### Using Docker (Recommended)

1. Configure environment variables in .env file
2. Build and run:
```bash
docker-compose up -d
```

### Manual Deployment

1. Configure environment variables
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the bot:
```bash
python bot.py
```

## Proxy Configuration

If you need to use a proxy:

1. Set proxy in .env file:
```env
HTTP_PROXY=http://your-proxy-server:port
HTTPS_PROXY=http://your-proxy-server:port
```

2. The Docker container will automatically use these proxy settings

## Maintenance

- Database is stored in `data/snapp.db`
- Logs are available in the console output
- Docker container automatically restarts on failure
- Token expiration is checked automatically

## Security Notes

- Never share your .env file
- Keep your bot token private
- Regularly check for expired tokens
- Monitor for unauthorized access

## Troubleshooting

1. Bot not responding:
   - Check if the bot is running
   - Verify BOT_TOKEN in .env
   - Check network connectivity

2. Database errors:
   - Ensure data directory exists
   - Check file permissions
   - Verify database integrity

3. Docker issues:
   - Check Docker logs
   - Verify environment variables
   - Ensure ports are not blocked

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details 