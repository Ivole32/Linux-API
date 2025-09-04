import os
from pathlib import Path
from typing import Optional, Dict

class ConfigLoader:
    """
    Configuration loader that reads from config.env file with environment variable fallback.
    """
    def __init__(self, config_file: str = "config.env"):
        self.config_file = Path(config_file)
        self._config: Optional[Dict[str, str]] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config.env file"""
        self._config = {}
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse key=value pairs
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self._config[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not read config file {self.config_file}: {e}")
                self._config = {}
    
    def get(self, key: str, default: str = '', fallback_to_env: bool = True) -> str:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            fallback_to_env: Whether to check environment variables if not found in config file
        
        Returns:
            Configuration value
        """
        if self._config is None:
            self._load_config()
        
        # First try config file
        if key in self._config:
            return self._config[key]
        
        # Then try environment variables if fallback is enabled
        if fallback_to_env:
            return os.getenv(key, default)
        
        return default
    
    def get_bool(self, key: str, default: bool = False, fallback_to_env: bool = True) -> bool:
        """
        Get configuration value as boolean.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            fallback_to_env: Whether to check environment variables if not found in config file
        
        Returns:
            Boolean configuration value
        """
        value = self.get(key, str(default).lower(), fallback_to_env)
        return value.lower() in ('true', '1', 'yes')

# Global configuration instance
_config_instance = None

def get_config(config_file: str = "config.env") -> ConfigLoader:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_file)
    return _config_instance