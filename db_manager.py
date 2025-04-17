import mysql.connector
from mysql.connector import pooling
import logging
from config import Config
import bcrypt
from functools import wraps
import time

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=Config.LOG_FILE
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        try:
            dbconfig = {
                "host": Config.DB_HOST,
                "user": Config.DB_USER,
                "password": Config.DB_PASSWORD,
                "database": Config.DB_NAME,
                "pool_name": "mypool",
                "pool_size": 5
            }
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self):
        try:
            return self._pool.get_connection()
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.rowcount
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_tables(self):
        try:
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    remember_me BOOLEAN DEFAULT FALSE,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    state VARCHAR(50),
                    city VARCHAR(50),
                    recommendedCrop VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''', fetch=False)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_user_data(self, username):
        try:
            result = self.execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get user data: {e}")
            return None
    
    def update_user_profile(self, username, email, phone, state, city):
        try:
            result = self.execute_query(
                """
                UPDATE users 
                SET email = %s, phone = %s, state = %s, city = %s 
                WHERE username = %s
                """,
                (email, phone, state, city, username),
                fetch=False
            )
            return result > 0
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    def update_recommendation(self, username, crop_name):
        try:
            result = self.execute_query(
                """
                UPDATE users 
                SET recommendedCrop = %s 
                WHERE username = %s
                """,
                (crop_name, username),
                fetch=False
            )
            return result > 0
        except Exception as e:
            logger.error(f"Failed to update recommendation: {e}")
            return False
    
    def authenticate_user(self, username, password):
        try:
            result = self.execute_query(
                "SELECT password FROM users WHERE username = %s",
                (username,)
            )
            if result and self.verify_password(password, result[0]['password']):
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def register_user(self, username, password):
        try:
            hashed_password = self.hash_password(password)
            result = self.execute_query(
                """
                INSERT INTO users 
                (username, password, email, phone, state, city, recommendedCrop) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (username, hashed_password, "", "", "", "", ""),
                fetch=False
            )
            return result > 0
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return False
    
    def update_remember_me(self, username, remember):
        try:
            result = self.execute_query(
                "UPDATE users SET remember_me = %s WHERE username = %s",
                (remember, username),
                fetch=False
            )
            return result > 0
        except Exception as e:
            logger.error(f"Failed to update remember_me: {e}")
            return False 