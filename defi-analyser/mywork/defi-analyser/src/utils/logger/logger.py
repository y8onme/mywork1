# src/utils/logger/logger.py

import logging
import sys
from typing import Dict, Optional
from datetime import datetime
import os
from pathlib import Path
import json
from ..config import config

class ChainLogger:
    def __init__(self):
        self.loggers: Dict[int, logging.Logger] = {}
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize loggers for each chain
        self._initialize_loggers()
        
        # Set up default logger
        self._setup_default_logger()
        
    def _initialize_loggers(self):
        """Initialize chain-specific loggers"""
        for chain_id in config.get_all_chain_ids():
            self._setup_chain_logger(chain_id)

    def _setup_chain_logger(self, chain_id: int):
        """Set up logger for specific chain"""
        try:
            # Create chain-specific logger
            logger = logging.getLogger(f"chain_{chain_id}")
            logger.setLevel(logging.DEBUG)
            
            # Create handlers
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            file_handler = logging.FileHandler(
                self.log_dir / f"chain_{chain_id}.log"
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatters
            console_formatter = logging.Formatter(
                '%(asctime)s [Chain %(chain_id)s] %(levelname)s: %(message)s'
            )
            
            file_formatter = logging.Formatter(
                '%(asctime)s [Chain %(chain_id)s] %(levelname)s '
                '[%(filename)s:%(lineno)d]: %(message)s'
            )
            
            # Set formatters
            console_handler.setFormatter(console_formatter)
            file_handler.setFormatter(file_formatter)
            
            # Add handlers
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            
            # Store logger
            self.loggers[chain_id] = logger
            
        except Exception as e:
            print(f"Error setting up chain logger: {str(e)}")
            raise

    def _setup_default_logger(self):
        """Set up default logger for non-chain-specific logs"""
        try:
            logger = logging.getLogger('default')
            logger.setLevel(logging.DEBUG)
            
            # Create handlers
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            file_handler = logging.FileHandler(
                self.log_dir / "default.log"
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatters
            console_formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            )
            
            file_formatter = logging.Formatter(
                '%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]: %(message)s'
            )
            
            # Set formatters
            console_handler.setFormatter(console_formatter)
            file_handler.setFormatter(file_formatter)
            
            # Add handlers
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            
            # Store logger
            self.loggers['default'] = logger
            
        except Exception as e:
            print(f"Error setting up default logger: {str(e)}")
            raise

    def info(self, message: str, chain_id: Optional[int] = None, **kwargs):
        """Log info message"""
        self._log('info', message, chain_id, **kwargs)

    def debug(self, message: str, chain_id: Optional[int] = None, **kwargs):
        """Log debug message"""
        self._log('debug', message, chain_id, **kwargs)

    def warning(self, message: str, chain_id: Optional[int] = None, **kwargs):
        """Log warning message"""
        self._log('warning', message, chain_id, **kwargs)

    def error(self, message: str, chain_id: Optional[int] = None, **kwargs):
        """Log error message"""
        self._log('error', message, chain_id, **kwargs)

    def critical(self, message: str, chain_id: Optional[int] = None, **kwargs):
        """Log critical message"""
        self._log('critical', message, chain_id, **kwargs)

    def _log(self, level: str, message: str, chain_id: Optional[int] = None, **kwargs):
        """Internal logging method"""
        try:
            # Get appropriate logger
            logger = self.loggers.get(
                chain_id if chain_id is not None else 'default'
            )
            
            if not logger:
                logger = self.loggers['default']
                
            # Add chain_id to extra
            extra = kwargs.get('extra', {})
            if chain_id is not None:
                extra['chain_id'] = chain_id
                
            # Get logging method
            log_method = getattr(logger, level)
            
            # Log message
            log_method(message, extra=extra)
            
        except Exception as e:
            print(f"Error logging message: {str(e)}")
            
            # Fallback to print
            print(f"[FALLBACK LOG] {level.upper()}: {message}")

    def log_transaction(self,
                       tx_hash: str,
                       chain_id: int,
                       status: str,
                       details: Dict):
        """Log transaction details"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'tx_hash': tx_hash,
                'chain_id': chain_id,
                'status': status,
                'details': details
            }
            
            # Log to chain-specific transaction log
            tx_log_path = self.log_dir / f"transactions_{chain_id}.json"
            
            # Read existing logs
            existing_logs = []
            if tx_log_path.exists():
                with open(tx_log_path, 'r') as f:
                    existing_logs = json.load(f)
                    
            # Append new log
            existing_logs.append(log_entry)
            
            # Write updated logs
            with open(tx_log_path, 'w') as f:
                json.dump(existing_logs, f, indent=2)
                
            # Also log to regular logger
            self.info(
                f"Transaction {tx_hash} {status}",
                chain_id=chain_id,
                extra={'tx_details': details}
            )
            
        except Exception as e:
            self.error(
                f"Error logging transaction: {str(e)}",
                chain_id=chain_id
            )

    def log_error(self,
                  error: Exception,
                  chain_id: Optional[int] = None,
                  context: Optional[Dict] = None):
        """Log error with context"""
        try:
            error_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'chain_id': chain_id,
                'context': context or {}
            }
            
            # Log to error log file
            error_log_path = self.log_dir / "errors.json"
            
            # Read existing logs
            existing_logs = []
            if error_log_path.exists():
                with open(error_log_path, 'r') as f:
                    existing_logs = json.load(f)
                    
            # Append new log
            existing_logs.append(error_entry)
            
            # Write updated logs
            with open(error_log_path, 'w') as f:
                json.dump(existing_logs, f, indent=2)
                
            # Also log to regular logger
            self.error(
                f"Error occurred: {str(error)}",
                chain_id=chain_id,
                extra={'error_context': context}
            )
            
        except Exception as e:
            print(f"Error logging error: {str(e)}")
            
            # Fallback to print
            print(f"[FALLBACK ERROR LOG] {str(error)}")

    def rotate_logs(self):
        """Rotate log files to prevent them from growing too large"""
        try:
            max_size = 10 * 1024 * 1024  # 10MB
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_size > max_size:
                    # Create backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = log_file.with_suffix(f".{timestamp}.log")
                    
                    # Rename current log to backup
                    log_file.rename(backup_path)
                    
                    # Create new log file
                    log_file.touch()
                    
                    # Reinitialize loggers
                    self._initialize_loggers()
                    
        except Exception as e:
            print(f"Error rotating logs: {str(e)}")

    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        try:
            current_time = datetime.now().timestamp()
            max_age = days * 24 * 60 * 60  # Convert days to seconds
            
            for log_file in self.log_dir.glob("*.log.*"):
                if current_time - log_file.stat().st_mtime > max_age:
                    log_file.unlink()
                    
        except Exception as e:
            print(f"Error cleaning up logs: {str(e)}")

# Initialize global logger instance
logger = ChainLogger()