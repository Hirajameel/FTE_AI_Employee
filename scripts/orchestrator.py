"""
Orchestrator for AI Employee (Bronze Tier)

This script:
1. Checks for files in Needs_Action folder
2. Triggers Qwen Code to process them
3. Updates the Dashboard.md with activity
4. Manages the overall workflow

For Bronze Tier, this is a simple trigger-based orchestrator.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import re


class Orchestrator:
    """
    Main orchestrator for the AI Employee.

    Coordinates between watchers, Qwen Code, and the vault.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for folder in [self.needs_action, self.plans, self.done, 
                       self.pending_approval, self.approved, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
        self.check_interval = check_interval
        
        # Track processed files
        self.processed_files = set()
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
    
    def _setup_logging(self):
        """Set up logging"""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def get_pending_files(self) -> List[Path]:
        """
        Get list of pending files in Needs_Action.
        
        Returns:
            List of file paths
        """
        try:
            files = [f for f in self.needs_action.iterdir() 
                    if f.is_file() and f.suffix == '.md' and f not in self.processed_files]
            return sorted(files, key=lambda f: f.stat().st_mtime)
        except Exception as e:
            self.logger.error(f'Error scanning Needs_Action: {e}')
            return []
    
    def count_pending_files(self) -> int:
        """Count pending files"""
        return len(self.get_pending_files())
    
    def update_dashboard(self, pending_count: int, completed_today: int = 0, 
                        pending_approval: int = 0, last_activity: str = '--'):
        """
        Update the Dashboard.md with current stats.
        
        Args:
            pending_count: Number of files in Needs_Action
            completed_today: Number of tasks completed today
            pending_approval: Number of items awaiting approval
            last_activity: Timestamp of last activity
        """
        try:
            if not self.dashboard.exists():
                self.logger.warning('Dashboard.md not found')
                return
            
            content = self.dashboard.read_text(encoding='utf-8')
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update last_updated in frontmatter
            content = re.sub(
                r'last_updated: .*',
                f'last_updated: {datetime.now().isoformat()}',
                content
            )
            
            # Update Quick Stats table
            stats_pattern = r'(\| Pending Tasks \|).*(\n\| Completed Today \|).*(\n\| Pending Approval \|)'
            stats_replacement = (
                f'\\1 {pending_count} \\2 {completed_today} \\3 {pending_approval}'
            )
            content = re.sub(stats_pattern, stats_replacement, content)
            
            # Update Last Activity
            content = re.sub(
                r'\*\*Last Activity:\*\* .*',
                f'**Last Activity:** {last_activity}',
                content
            )
            
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.debug('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def trigger_qwen(self, files: List[Path]) -> bool:
        """
        Trigger Qwen Code to process pending files.

        For Bronze Tier, this creates a prompt file that can be
        manually triggered or integrated with Qwen Code.

        Args:
            files: List of files to process

        Returns:
            True if successful
        """
        if not files:
            return True
        
        try:
            # Create a prompt file for Qwen Code
            prompt_file = self.vault_path / '.qwen_prompt.md'

            file_list = '\n'.join([f'- `{f.name}`' for f in files])

            prompt_content = f'''# AI Employee Task Queue

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files to Process

{file_list}

## Instructions for Qwen Code

1. Read each file in the Needs_Action folder listed above
2. Analyze the content and determine required actions
3. Create a Plan.md file in /Plans/ with checkboxes for multi-step tasks
4. For actions requiring approval, create files in /Pending_Approval/
5. For simple tasks, process and move to /Done/
6. Update Dashboard.md with activity summary
7. Log all actions to /Logs/

## Company Handbook Reference

Review `/Company_Handbook.md` for rules and guidelines before taking action.

## Business Goals Reference

Review `/Business_Goals.md` for current objectives and metrics.

---

**Status:** Ready for processing
'''

            prompt_file.write_text(prompt_content, encoding='utf-8')
            self.logger.info(f'Created Qwen prompt: {prompt_file}')

            # Try to run Qwen Code if available
            qwen_available = self._check_qwen_available()

            if qwen_available:
                self.logger.info('Qwen Code detected - ready to process')
                # Note: In Bronze tier, user manually runs Qwen Code
                # Full automation requires Ralph Wiggum loop setup
            else:
                self.logger.info('Qwen Code not detected - please run manually')
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error triggering Qwen: {e}')
            return False
    
    def _check_qwen_available(self) -> bool:
        """Check if Qwen Code is available"""
        try:
            result = subprocess.run(
                ['qwen', '--version'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run_qwen_code(self, prompt: str = None):
        """
        Run Qwen Code with a specific prompt.

        Args:
            prompt: Optional prompt to pass to Qwen
        """
        try:
            cmd = ['qwen']
            if prompt:
                cmd.extend(['--prompt', prompt])
            cmd.extend(['--cwd', str(self.vault_path)])

            self.logger.info(f'Running Qwen Code: {" ".join(cmd)}')

            # Run in foreground for Bronze tier
            subprocess.run(cmd, cwd=self.vault_path)

        except FileNotFoundError:
            self.logger.error('Qwen Code not found. Please install Qwen Code.')
        except Exception as e:
            self.logger.error(f'Error running Qwen Code: {e}')
    
    def process_completed(self) -> int:
        """
        Move processed files to Done folder.
        
        Returns:
            Number of files moved
        """
        moved = 0
        done_today = self.done / datetime.now().strftime("%Y-%m-%d")
        done_today.mkdir(exist_ok=True)
        
        # This would be called after Claude processes files
        # For now, it's a placeholder for the workflow
        return moved
    
    def run_once(self) -> dict:
        """
        Run a single orchestration cycle.
        
        Returns:
            Dictionary with run statistics
        """
        stats = {
            'timestamp': datetime.now().isoformat(),
            'pending_files': 0,
            'processed': 0,
            'errors': 0
        }
        
        try:
            # Check for pending files
            pending = self.get_pending_files()
            stats['pending_files'] = len(pending)
            
            if pending:
                self.logger.info(f'Found {len(pending)} pending file(s)')

                # Trigger Qwen
                if self.trigger_qwen(pending):
                    stats['processed'] = len(pending)
                    self.update_dashboard(
                        pending_count=len(pending),
                        last_activity=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                else:
                    stats['errors'] = 1
            else:
                self.logger.debug('No pending files')
                self.update_dashboard(pending_count=0)
            
        except Exception as e:
            self.logger.error(f'Error in orchestration cycle: {e}')
            stats['errors'] += 1
        
        return stats
    
    def run(self):
        """
        Main run loop.
        
        Continuously monitors and processes files.
        """
        import time
        
        self.logger.info('Starting Orchestrator')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )
    parser.add_argument(
        '--run-qwen',
        action='store_true',
        help='Run Qwen Code immediately'
    )
    
    args = parser.parse_args()
    
    # Resolve vault path
    vault_path = Path(args.vault).resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        print('Please create the vault directory first.')
        return 1
    
    orchestrator = Orchestrator(
        vault_path=str(vault_path),
        check_interval=args.interval
    )
    
    if args.run_qwen:
        prompt_file = vault_path / '.qwen_prompt.md'
        if prompt_file.exists():
            prompt = prompt_file.read_text(encoding='utf-8')
            orchestrator.run_qwen_code(prompt)
        else:
            orchestrator.run_qwen_code('Process all files in Needs_Action folder')
        return 0
    
    if args.once:
        stats = orchestrator.run_once()
        print(f'Orchestration complete:')
        print(f'  Pending files: {stats["pending_files"]}')
        print(f'  Processed: {stats["processed"]}')
        print(f'  Errors: {stats["errors"]}')
        return 0 if stats['errors'] == 0 else 1
    
    orchestrator.run()
    return 0


if __name__ == '__main__':
    exit(main())
