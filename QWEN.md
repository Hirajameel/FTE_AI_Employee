# Personal AI Employee (FTE) Project

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI agent that manages personal and business affairs 24/7. The architecture is **local-first**, **agent-driven**, and uses **human-in-the-loop** safeguards.

### Core Concept

The AI Employee acts as a proactive business partner that:
- Monitors communication channels (Gmail, WhatsApp, LinkedIn)
- Manages tasks and projects via Obsidian Markdown vaults
- Handles accounting and bank transaction auditing
- Generates "Monday Morning CEO Briefings" with revenue reports and bottleneck analysis
- Posts to social media platforms autonomously

### Architecture & Tech Stack

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian | Local Markdown dashboard and knowledge base |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems to trigger AI |
| **Hands** | MCP Servers | Model Context Protocol for external actions (email, payments, browser automation) |
| **Browser** | Playwright | Web automation for form filling, clicking, screenshots |

### Key Architectural Patterns

1. **Watcher Pattern**: Lightweight Python scripts run continuously, monitoring inputs and creating `.md` files in `/Needs_Action/` folder
2. **File-Based Workflow**: Tasks flow through folders: `/Needs_Action/` → `/Plans/` → `/Pending_Approval/` → `/Approved/` → `/Done/`
3. **Human-in-the-Loop (HITL)**: Sensitive actions require approval before execution
4. **Ralph Wiggum Loop**: A Stop hook pattern that keeps Claude iterating until tasks are complete

## Directory Structure

```
FTE_AI_Employee/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main hackathon blueprint
├── skills-lock.json          # Qwen skills configuration
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/  # Browser automation skill
│           ├── SKILL.md
│           ├── references/
│           └── scripts/
│               ├── mcp-client.py       # MCP client for Playwright
│               ├── start-server.sh     # Start Playwright MCP server
│               ├── stop-server.sh      # Stop Playwright MCP server
│               └── verify.py           # Server verification script
└── .git/
```

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_...md` | Comprehensive 1200+ line blueprint with architecture, templates, security guidelines, and learning resources |
| `skills-lock.json` | Qwen skills registry (currently includes browsing-with-playwright) |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Playwright MCP usage documentation |

## Building & Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |
| GitHub Desktop | Latest | Version control |

### Setup Steps

1. **Create Obsidian Vault** named `AI_Employee_Vault` with folders:
   - `/Inbox/`, `/Needs_Action/`, `/Plans/`, `/Done/`, `/Pending_Approval/`, `/Approved/`, `/Logs/`

2. **Verify Claude Code**:
   ```bash
   claude --version
   ```

3. **Set up Python environment** (UV recommended)

4. **Configure MCP servers** in `~/.config/claude-code/mcp.json`

5. **Start Playwright MCP** (when browser automation needed):
   ```bash
   bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
   ```

### Running Watchers (Example)

```bash
# Gmail Watcher
python gmail_watcher.py

# WhatsApp Watcher (Playwright-based)
python whatsapp_watcher.py

# File System Watcher
python filesystem_watcher.py
```

### Process Management (Production)

Use PM2 to keep watchers alive:
```bash
npm install -g pm2
pm2 start gmail_watcher.py --interpreter python3
pm2 save
pm2 startup
```

## Development Conventions

### Coding Style
- Python scripts follow the `BaseWatcher` abstract class pattern
- All watchers implement `check_for_updates()` and `create_action_file()` methods
- Use environment variables for credentials (never hardcode)
- Support `--dry-run` flag for all action scripts

### Security Practices
- **Never commit `.env` files** (add to `.gitignore`)
- Use `DRY_RUN` mode during development
- Implement audit logging in `/Vault/Logs/YYYY-MM-DD.json`
- Rotate credentials monthly
- All payments and sensitive actions require HITL approval

### Testing Practices
- Test watchers in isolation with mock data
- Verify MCP server connectivity before production use
- Run `python3 scripts/verify.py` for Playwright MCP verification

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hours | Obsidian dashboard, one watcher, Claude Code integration |
| **Silver** | 20-30 hours | Multiple watchers, MCP server, HITL workflow, scheduling |
| **Gold** | 40+ hours | Full integration, Odoo accounting, social media, Ralph Wiggum loop |
| **Platinum** | 60+ hours | Cloud deployment, delegation, 24/7 always-on operation |

## Learning Resources

### Prerequisites (Complete Before Hackathon)
- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Fundamentals](https://help.obsidian.md/Getting+started)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Core Learning
- [Claude + Obsidian Integration](https://www.youtube.com/watch?v=sCIS05Qt79Y)
- [Building MCP Servers](https://modelcontextprotocol.io/quickstart)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [Playwright Automation](https://playwright.dev/python/docs/intro)

## Weekly Meetings

**Research & Showcase**: Wednesdays at 10:00 PM PKT on Zoom
- First meeting: Wednesday, January 7th, 2026
- [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- [YouTube Backup](https://www.youtube.com/@panaversity)

## Submission

- **Form**: [https://forms.gle/JR9T1SJq5rmQyGkGA](https://forms.gle/JR9T1SJq5rmQyGkGA)
- **Requirements**: GitHub repo, README.md, demo video (5-10 min), security disclosure
