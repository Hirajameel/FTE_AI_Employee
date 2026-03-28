# AI Employee Scripts

Python scripts for the AI Employee (Bronze Tier) automation system.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Python Version

Requires Python 3.13 or higher.

## Scripts

### 1. File System Watcher (`filesystem_watcher.py`)

Monitors a drop folder for new files and creates action files in the Needs_Action folder.

**Usage:**
```bash
# Run continuously
python filesystem_watcher.py --vault ../AI_Employee_Vault

# Run once (for testing or cron)
python filesystem_watcher.py --vault ../AI_Employee_Vault --once

# Custom drop folder
python filesystem_watcher.py --vault ../AI_Employee_Vault --drop-folder /path/to/drop
```

**Options:**
- `--vault`: Path to Obsidian vault (default: ../AI_Employee_Vault)
- `--drop-folder`: Folder to monitor (default: vault/Drop)
- `--interval`: Check interval in seconds (default: 30)
- `--once`: Run once and exit

### 2. Orchestrator (`orchestrator.py`)

Coordinates between watchers and Qwen Code.

**Usage:**
```bash
# Run continuously
python orchestrator.py --vault ../AI_Employee_Vault

# Run once
python orchestrator.py --vault ../AI_Employee_Vault --once

# Trigger Qwen Code immediately
python orchestrator.py --vault ../AI_Employee_Vault --run-qwen
```

**Options:**
- `--vault`: Path to Obsidian vault
- `--interval`: Check interval in seconds (default: 60)
- `--once`: Run once and exit
- `--run-qwen`: Run Qwen Code immediately

## Quick Start

1. **Start the File Watcher:**
   ```bash
   cd scripts
   python filesystem_watcher.py --vault ../AI_Employee_Vault
   ```

2. **In another terminal, start the Orchestrator:**
   ```bash
   cd scripts
   python orchestrator.py --vault ../AI_Employee_Vault
   ```

3. **Drop a file into the vault/Drop folder:**
   ```bash
   echo "Process this task" > ../AI_Employee_Vault/Drop/test.txt
   ```

4. **Check the Needs_Action folder** - a new action file should be created.

5. **Run Qwen Code** to process the action:
   ```bash
   cd ../AI_Employee_Vault
   qwen --prompt "Process all files in Needs_Action folder"
   ```

## Production Deployment

For continuous operation, use a process manager like PM2:

```bash
# Install PM2
npm install -g pm2

# Start watchers
pm2 start filesystem_watcher.py --interpreter python3 -- --vault /path/to/vault
pm2 start orchestrator.py --interpreter python3 -- --vault /path/to/vault

# Save configuration
pm2 save

# Set up startup
pm2 startup
```

## Logs

Logs are stored in:
- `vault/Logs/YYYY-MM-DD.log` - Watcher logs
- `vault/Logs/orchestrator_YYYY-MM-DD.log` - Orchestrator logs

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Vault not found" error
Ensure the vault path is correct and the directory exists.

### Qwen Code not detected
Make sure Qwen Code is installed and available in your PATH.

## Architecture

```
┌─────────────────────┐
│  File System        │
│  Watcher            │
│  (filesystem_       │
│   watcher.py)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Needs_Action/      │
│  (Markdown files)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Orchestrator       │
│  (orchestrator.py)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Qwen Code          │
│  (Processing)       │
└─────────────────────┘
```
