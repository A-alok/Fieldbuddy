import os
import json
import logging
import hashlib
import time
from functools import wraps
from config import Config
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Cache:
    _cache: Dict[str, Any] = {}
    _timestamps: Dict[str, float] = {}
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._cache:
            if time.time() - cls._timestamps[key] < Config.CACHE_TTL:
                return cls._cache[key]
            else:
                del cls._cache[key]
                del cls._timestamps[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._cache[key] = value
        cls._timestamps[key] = time.time()
    
    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()
        cls._timestamps.clear()

def cache_result(ttl: int = Config.CACHE_TTL):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not Config.CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = Cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            Cache.set(key, result)
            return result
        return wrapper
    return decorator

def validate_input(data: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
    """Validate input data against required fields"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, ""

def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent SQL injection"""
    return data.replace("'", "''").replace(";", "")

def get_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        Config.IMAGES_DIR,
        Config.DATA_DIR,
        os.path.dirname(Config.LOG_FILE)
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def download_file(url: str, save_path: str) -> bool:
    """Download a file from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        return False

def load_json_file(file_path: str) -> Dict:
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file: {e}")
        return {}

def save_json_file(data: Dict, file_path: str) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file: {e}")
        return False

def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        last_called = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            if key in last_called:
                time_since_last_call = current_time - last_called[key]
                if time_since_last_call < 60 / requests_per_minute:
                    time.sleep(60 / requests_per_minute - time_since_last_call)
            
            last_called[key] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator 