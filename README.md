# OpenClaw Recovery Guide

This folder contains your complete OpenClaw setup for Vayu-2.0.

## What's Included

- `openclaw.json` — Gateway configuration (Discord bot token, models, settings)
- `AGENTS.md`, `SOUL.md`, `IDENTITY.md` — Vayu's personality and behavior
- `USER.md` — Your profile and preferences
- `BOOTSTRAP.md`, `HEARTBEAT.md`, `TOOLS.md` — Operational configuration
- `openclaw-backup.json` — Backup of the main config

## Quick Recovery Steps

### 1. Install OpenClaw (if needed)

```bash
npm install -g openclaw
```

### 2. Restore Configuration

```bash
# Create OpenClaw directory if it doesn't exist
mkdir -p ~/.openclaw

# Copy main config
cp ~/claw/openclaw.json ~/.openclaw/openclaw.json

# Copy workspace files
cp -r ~/claw/AGENTS.md ~/claw/SOUL.md ~/claw/IDENTITY.md ~/claw/USER.md ~/claw/BOOTSTRAP.md ~/claw/HEARTBEAT.md ~/claw/TOOLS.md ~/.openclaw/workspace/ 2>/dev/null || mkdir -p ~/.openclaw/workspace && cp ~/claw/*.md ~/.openclaw/workspace/
```

### 3. Re-authenticate API Keys

These are stored separately in `~/.openclaw/.env` (not included here for security):

```bash
# Set up Moonshot API key
openclaw configure --section auth
# Choose: moonshot → API key mode
# Enter your Moonshot API key

# Set up Gemini API key (for nano-banana-pro skill)
openclaw configure --section skills
# Or edit ~/.openclaw/.env directly:
# MOONSHOT_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
```

### 4. Start the Gateway

```bash
openclaw gateway start
```

Or restart if already running:

```bash
openclaw gateway restart
```

### 5. Verify Connection

Once the Gateway is running, tag Vayu in Discord:

```
<@1467358480737243399> status
```

You should get a response.

## Important Notes

- **Discord Bot Token**: Already configured in `openclaw.json`. The bot will reconnect automatically when the Gateway starts.
- **WhatsApp**: If configured, you'll need to re-scan the QR code after restart (check `openclaw whatsapp login`).
- **Memory**: Long-term memories are in `memory/` folder (check if you have a `memory/` subfolder to copy too).

## Troubleshooting

**Gateway won't start?**
- Check if port 18789 is free: `lsof -i :18789`
- Check logs: `openclaw gateway logs` or `~/.openclaw/logs/`

**Bot not responding?**
- Verify Gateway is running: `openclaw gateway status`
- Check Discord bot is online in your server
- Try: `openclaw gateway restart`

**Missing API keys?**
- Run `openclaw configure --section auth` to re-enter them
- Or check `~/.openclaw/.env` exists with the right variables

## Contact

If Vayu is online: just ask.
Otherwise: Check OpenClaw docs at https://docs.openclaw.ai
