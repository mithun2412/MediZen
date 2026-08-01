# instance_config.py
import os
import sys

def get_instance_config(port):
    """Get configuration for a specific instance"""
    
    # Base configuration
    config = {
        "PORT": port,
        "HOST": "0.0.0.0",
    }
    
    # Different database for each instance (if using SQLite)
    if os.getenv("DATABASE_URL", "").startswith("sqlite"):
        # Use separate SQLite files
        config["DATABASE_URL"] = f"sqlite:///./medivoice_{port}.db"
    
    # Different log file for each instance
    config["LOG_FILE"] = f"logs/medizen_{port}.log"
    
    return config