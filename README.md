# FlyMe - A Real-Time Slack Bot for Flights!

FlyMe is an agentic helper that will search for flights for you directly in Slack! Just ask FlyMe for flights via DM or with an @mention in natural language, and it'll connect to Arcade.dev, OpenAI, and Google Flights to pull down some options!

## Prerequisites

- Python 3.8+
- Slack workspace admin access
- Arcade.dev account
- OpenAI API key

## Installation

### Clone the Repository
   ```bash
   git clone https://github.com/KristopherLeads/flyme
   cd flyme
   ```

### Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Create `.env` File
   ```bash
   ARCADE_API_KEY=your_arcade_api_key
   OPENAI_API_KEY=your_openai_api_key
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```

## Slack App Setup

### Create a Slack App
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App" > "From scratch"
   - Name: `FlyMe`

### Enable Socket Mode
   - Settings > Socket Mode > Enable
   - Generate app-level token with `connections:write` scope
   - Save token as `SLACK_APP_TOKEN`

### Configure OAuth & Permissions

   - Add Bot Token Scopes:
     - `chat:write`
     - `channels:read`
     - `im:read`
     - `im:write`
     - `im:history`
     - `users:read`
   - Install to workspace
   - Save Bot User OAuth Token as `SLACK_BOT_TOKEN`

### Enable Event Subscriptions

   - Turn on Events
   - Subscribe to bot events:
     - `message.im`
     - `app_mention`

### Enable Messages Tab

   - Enable this via App Home > Messages Tab > Enable

## Usage

### Start the Bot

   ```bash
   python3 main.py
   ```

### Interact on Slack

   - DM the bot: "Find me flights from NYC to LA next month"
   - Or @mention in a channel: "@FlyMe flights to Miami tomorrow"

## File Structure

```
flyme/
├── app.py             # FlyMe orchestration logic
├── bot.py             # FlyMeBot class
├── config.py          # FlyMe configuration management
├── constants.py       # FlyMe application constants
├── graceful.py        # Graceful shutdown handling
├── slack.py           # Slack integration
├── main.py            # Core FlyMe application
├── instructions.md    # AI agent instructions
├── requirements.txt   # Dependencies
├── LICENSE            # MIT license
├── README.md          # Documentation
├── .env.example       # Example environment variables
└── .gitignore         # Git ignore file
```

## Customization

Edit `instructions.md` to modify bot behavior. This file is sent to OpenAI for instructions, so you can fully customize this tool in any way you'd like!

## Troubleshooting

### Bot not responding?
- Verify Socket Mode is enabled
- Check all 4 environment variables are set
- Ensure bot is invited to channels and is given perms in Slack Apps

### No flight results?
- Try major airport codes (JFK, LAX, ORD)

### Missing instructions.md?
- The bot requires this file to run - redownload from the repo

## License

MIT

## Thank You
Thanks to GitHub for the include Python `.gitignore` [template](https://github.com/github/gitignore/tree/main).
