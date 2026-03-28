"""
Base Watcher Abstract Class

All watcher implementations should inherit from this class.
Watchers monitor external sources (Gmail, WhatsApp, filesystems) 
and create action files in the Needs_Action folder.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional
import hashlib


class BaseWatcher(ABC):
    """Abstract base class for all watchers"""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
    def _setup_logging(self):
        """Set up logging to file and console"""
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items from the monitored source.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if failed
        """
        pass
    
    def _generate_unique_id(self, content: str) -> str:
        """Generate a unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _create_markdown_file(self, filename: str, content: str) -> Path:
        """
        Create a markdown file in Needs_Action folder.
        
        Args:
            filename: Name of the file (without extension)
            content: Markdown content
            
        Returns:
            Path to created file
        """
        filepath = self.needs_action / f'{filename}.md'
        
        # Add timestamp if file exists
        if filepath.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.needs_action / f'{filename}_{timestamp}.md'
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filepath}')
        return filepath
    
    def run(self):
        """
        Main run loop. Continuously monitors for updates.
        
        Press Ctrl+C to stop.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            self.create_action_file(item)
                    else:
                        self.logger.debug('No new items')
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
    
    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing or cron jobs).
        
        Returns:
            Number of items processed
        """
        items = self.check_for_updates()
        for item in items:
            self.create_action_file(item)
        return len(items)


class WatcherError(Exception):
    """Base exception for watcher errors"""
    pass


class AuthenticationError(WatcherError):
    """Authentication failed"""
    pass


class ConnectionError(WatcherError):
    """Connection to source failed"""
    pass
