# ShigureCafeBot

A Telegram bot for ShigureCafe user audit workflow.

## Features

- Receive audit codes from users in private chat.
- Verify audit codes via Backend API.
- Generate one-time, 10-minute temporary invite links for the audit group.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and configurations
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Configuration

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
- `BACKEND_URL`: URL to your ShigureCafeBackend (e.g., `http://localhost:8080`).
- `CAFE_API_KEY`: API Key for ShigureCafeBackend.
- `AUDIT_GROUP_ID`: The Telegram Chat ID of your audit group. The bot must be an administrator in this group with "Invite Users via Link" permission.
