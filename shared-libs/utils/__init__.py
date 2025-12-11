"""
Utilities - Shared Library

Provides common utilities, helpers, and cross-cutting concerns
for all TuringMachines services.
"""

from typing import Dict, Any, Optional
import logging
import hashlib
import json
from datetime import datetime


class Logger:
    """Centralized logging with structured format."""
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get configured logger instance."""
        logger = logging.getLogger(name)
        
        # Configure if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger


class Crypto:
    """Cryptographic utilities."""
    
    @staticmethod
    def hash_sha256(data: str) -> str:
        """
        Generate SHA256 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            Hex-encoded hash
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """
        Generate unique identifier.
        
        Args:
            prefix: Optional prefix for ID
            
        Returns:
            Unique identifier
        """
        timestamp = datetime.utcnow().isoformat()
        hash_val = Crypto.hash_sha256(timestamp)[:8]
        return f"{prefix}_{hash_val}" if prefix else hash_val


class Serialization:
    """Serialization utilities."""
    
    @staticmethod
    def to_json(data: Any) -> str:
        """
        Serialize data to JSON.
        
        Args:
            data: Data to serialize
            
        Returns:
            JSON string
        """
        return json.dumps(data, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> Any:
        """
        Deserialize JSON to data.
        
        Args:
            json_str: JSON string
            
        Returns:
            Deserialized data
        """
        return json.loads(json_str)


class Validation:
    """Data validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        return "@" in email and "." in email.split("@")[1]
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid
        """
        # Basic validation: at least 10 digits
        digits = "".join(c for c in phone if c.isdigit())
        return len(digits) >= 10
    
    @staticmethod
    def validate_amount(amount: float, min_val: float = 0.0,
                       max_val: float = 1000000.0) -> bool:
        """
        Validate transaction amount.
        
        Args:
            amount: Transaction amount
            min_val: Minimum allowed amount
            max_val: Maximum allowed amount
            
        Returns:
            True if valid
        """
        return min_val <= amount <= max_val


class Config:
    """Configuration management utilities."""
    
    _config: Dict[str, Any] = {}
    
    @classmethod
    def load(cls, config_dict: Dict[str, Any]) -> None:
        """Load configuration."""
        cls._config = config_dict
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return cls._config.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set configuration value."""
        cls._config[key] = value


__all__ = [
    "Logger",
    "Crypto",
    "Serialization",
    "Validation",
    "Config"
]
