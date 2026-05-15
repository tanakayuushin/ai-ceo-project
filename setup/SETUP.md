# Allen AI CEO - Full Setup Guide

New PC setup: follow ALL steps in order.
After git pull on existing PC: run verify.ps1 only.

---

## Prerequisites (install before anything else)

### 1. Git
https://git-scm.com/download/win
Verify: `git --version`

### 2. Node.js (LTS)
https://nodejs.org/
Verify: `node --version` and `npm --version`

### 3. Python 3.x
https://www.python.org/downloads/
Check "Add Python to PATH" during install.
Verify: `python --version`

### 4. Claude Code CLI
```
npm install -g @anthropic-ai/claude-code
```
Verify: `claude --version`

---

## Step 1: Clone repository

```powershell
git clone https://github.com/tanakayuushin/ai-ceo-project.git
cd ai-ceo-project
```

---

## Step 2: Run setup script (installs Allen memory)

```powershell
cd setup
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Automatically sets up:
- Security hooks (layer2-5) - already in repo, referenced directly
- Auto-approval (bypassPermissions) - already in .claude/settings.json
- Allen memory (20 files) - copied to ~/.claude/projects/.../memory/

---

## Step 3: Verify setup

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

All items must show [OK]. If [NG] appears, run install.ps1 again.

---

## Step 4: Set API keys

Create `.env` file in the repo root:

```
ANTHROPIC_API_KEY=sk-ant-...
NOTION_TOKEN=...
NOTION_PAGE_ID=...
X_CONSUMER_KEY=...
X_CONSUMER_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

Get keys from:
- Anthropic API key: https://console.anthropic.com/
- X (Twitter) API: https://developer.twitter.com/
- Notion: https://www.notion.so/my-integrations

---

## Step 5: Set up MCP servers

Start Claude Code first (`claude`), then run these commands inside Claude Code:

### Playwright (browser automation)
```
/mcp
```
Then add:
- Name: playwright
- Command: npx @playwright/mcp@latest

Or from terminal:
```
claude mcp add playwright npx @playwright/mcp@latest
```

### Gmail
```
claude mcp add --transport http gmail https://gmailmcp.googleapis.com/mcp/v1
```
Note: Google account authentication required on first use.

---

## Step 6: Start Claude Code and verify

```powershell
cd ..
claude
```

Send this in Claude Code chat:
```
git status
```
If no approval dialog appears, auto-approval is working.

Then send:
```
Allen, briefing please.
```

---

## After git pull (existing PC)

```powershell
git pull
cd setup
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

If [NG] items appear:
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

Restart Claude Code after install.ps1.

---

## Feature summary

| Feature | Setup method |
|---------|-------------|
| Auto-approval | git pull (in .claude/settings.json) |
| Security hooks (layer2-5) | git pull (in setup/hooks/) |
| Allen memory (20 files) | install.ps1 |
| CLAUDE.md (company rules) | git pull |
| Playwright MCP | claude mcp add (manual, Step 5) |
| Gmail MCP | claude mcp add (manual, Step 5) |
| API keys (X, Notion, Anthropic) | .env file (manual, Step 4) |

---

## Folder structure

```
setup/
+-- SETUP.md              # This guide
+-- install.ps1           # Setup script (copies memory files)
+-- verify.ps1            # Verification script (run after git pull)
+-- settings_template.json
+-- hooks/                # Security hooks (4 layers)
|   +-- layer2_bash_guard.py
|   +-- layer3_secrets_guard.py
|   +-- layer4_file_guard.py
|   +-- layer5_audit_log.py
+-- memory/               # Allen memory files (20 files)
    +-- MEMORY.md
    +-- project_ai_ceo.md
    +-- feedback_ceo_rules.md
    +-- ... (17 more files)
```

---

## Troubleshooting

**"python not found"**
Reinstall Python and check "Add to PATH".

**Commands still ask for approval**
Restart Claude Code. Settings load at startup.

**Memory not loading**
Re-run install.ps1. Check that verify.ps1 shows memory count >= 10.

**MCP not connecting**
Run `claude mcp list` to check connection status.