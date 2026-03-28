"""
File System Watcher

Monitors a drop folder for new files and creates action files
in the Needs_Action folder for Claude Code to process.

This is the simplest watcher to set up - just drop files into
the monitored folder and the AI Employee will process them.
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher


class FileDropWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is detected, it:
    1. Copies the file to the vault
    2. Creates a metadata .md file in Needs_Action
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the file drop watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            drop_folder: Path to the folder to monitor (default: vault/Drop)
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Drop'
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash
        self.processed_files = self._load_processed_files()
        
        # Keywords to detect priority
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'contract', 'deadline']
        
        self.logger.info(f'Monitoring drop folder: {self.drop_folder}')
    
    def _load_processed_files(self) -> set:
        """Load set of already processed file hashes"""
        cache_file = self.vault_path / '.processed_files.cache'
        if cache_file.exists():
            try:
                content = cache_file.read_text()
                return set(content.strip().split('\n')) if content.strip() else set()
            except Exception as e:
                self.logger.warning(f'Could not load processed files cache: {e}')
        return set()
    
    def _save_processed_files(self):
        """Save processed file hashes to cache"""
        cache_file = self.vault_path / '.processed_files.cache'
        try:
            # Keep only last 1000 entries
            hashes = list(self.processed_files)[-1000:]
            cache_file.write_text('\n'.join(hashes))
        except Exception as e:
            self.logger.warning(f'Could not save processed files cache: {e}')
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _detect_priority(self, filename: str, content: str = '') -> str:
        """Detect priority level based on filename and content"""
        text = f'{filename} {content}'.lower()
        
        for keyword in self.priority_keywords:
            if keyword in text:
                return 'high'
        
        return 'normal'
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of file info dictionaries
        """
        new_files = []
        
        try:
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_hash = self._calculate_file_hash(filepath)
                    
                    if file_hash not in self.processed_files:
                        self.logger.info(f'New file detected: {filepath.name}')
                        new_files.append({
                            'path': filepath,
                            'hash': file_hash,
                            'name': filepath.name,
                            'size': filepath.stat().st_size,
                            'modified': datetime.fromtimestamp(filepath.stat().st_mtime)
                        })
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            file_info: Dictionary with file information
            
        Returns:
            Path to created action file
        """
        try:
            filepath = file_info['path']
            filename = file_info['name']
            file_hash = file_info['hash']
            file_size = file_info['size']
            modified = file_info['modified']
            
            # Copy file to vault storage
            storage_folder = self.vault_path / 'Attachments'
            storage_folder.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f'{timestamp}_{filename}'
            dest_path = storage_folder / safe_filename
            
            shutil.copy2(filepath, dest_path)
            self.logger.info(f'Copied file to vault: {dest_path}')
            
            # Detect priority
            priority = self._detect_priority(filename)
            
            # Read file content if text-based
            content_preview = ''
            if filepath.suffix.lower() in ['.txt', '.md', '.json', '.csv', '.log']:
                try:
                    content_preview = filepath.read_text(encoding='utf-8')[:500]
                except Exception:
                    content_preview = '[Binary file or could not read]'
            
            # Create action file
            action_content = f'''---
type: file_drop
source_file: {filename}
stored_path: {dest_path}
size: {file_size}
detected: {datetime.now().isoformat()}
modified: {modified.isoformat()}
priority: {priority}
status: pending
hash: {file_hash}
---

# File Drop for Processing

## Source File
- **Name:** {filename}
- **Size:** {file_size:,} bytes
- **Stored at:** `Attachments/{safe_filename}`
- **Detected:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Content Preview
```
{content_preview if content_preview else '[No preview available - binary file]'}
```

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
<!-- Add notes here -->

'''
            
            # Generate filename
            base_name = Path(filename).stem
            action_filename = f'FILE_DROP_{base_name}_{timestamp}'
            
            action_file = self._create_markdown_file(action_filename, action_content)
            
            # Mark as processed
            self.processed_files.add(file_hash)
            self._save_processed_files()
            
            # Optionally remove from drop folder after processing
            # Uncomment the next line to auto-clean drop folder
            # filepath.unlink()
            
            return action_file
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}', exc_info=True)
            return None


def main():
    """Run the file drop watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description='File Drop Watcher for AI Employee')
    parser.add_argument(
        '--vault', 
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--drop-folder',
        type=str,
        default=None,
        help='Path to drop folder (default: vault/Drop)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing/cron)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    vault_path = Path(args.vault).resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault not found at {vault_path}')
        return 1
    
    watcher = FileDropWatcher(
        vault_path=str(vault_path),
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    
    if args.once:
        count = watcher.run_once()
        print(f'Processed {count} file(s)')
        return 0
    else:
        watcher.run()
        return 0


if __name__ == '__main__':
    exit(main())
