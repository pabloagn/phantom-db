#!/usr/bin/env python3
"""
Configuration parser for the phantom project.
Handles reading credentials and configuration from TOML files.
"""
import os
import tomli
from typing import Dict, Any, Optional

class ConfigParser:
    """Parser for TOML configuration files."""
    
    def __init__(self, config_path: str = None):
        """Initialize the config parser with optional path."""
        if config_path is None:
            # Default to the config directory in project root
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config', 
                'credentials.toml'
            )
        else:
            self.config_path = config_path
            
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from TOML file."""
        try:
            with open(self.config_path, "rb") as f:
                return tomli.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")
    
    def get_db_credentials(self, db_key: str = 'phantom-db') -> Dict[str, Any]:
        """Get database credentials for the specified database key."""
        try:
            db_config = self.config['database'][db_key]
            admin_config = self.config['users']['admin']
            
            return {
                'host': db_config['host'],
                'port': db_config['port'],
                'database': db_config['name'],
                'user': admin_config['username'],
                'password': admin_config['password'],
                'client_encoding': 'UTF8'
            }
        except KeyError as e:
            raise KeyError(f"Missing required configuration key: {str(e)}")
    
    def get_connection_string(self, db_key: str = 'phantom-db') -> str:
        """Get a formatted connection string for the specified database."""
        creds = self.get_db_credentials(db_key)
        return f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"