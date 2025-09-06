"""
Database connection configuration and utilities
Handles PostgreSQL connections with connection pooling
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'campus_events')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'kv2k04')
        self.port = os.getenv('DB_PORT', '5432')
        self.min_conn = int(os.getenv('DB_MIN_CONN', '1'))
        self.max_conn = int(os.getenv('DB_MAX_CONN', '20'))
        
        # Connection string
        self.connection_string = f"host={self.host} dbname={self.database} user={self.user} password={self.password} port={self.port}"

class DatabaseManager:
    """Database manager with connection pooling"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.config.min_conn,
                self.config.max_conn,
                host=self.config.host,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                port=self.config.port,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def return_connection(self, connection):
        """Return connection to pool"""
        try:
            self.connection_pool.putconn(connection)
        except Exception as e:
            logger.error(f"Failed to return database connection: {e}")
    
    def close_all_connections(self):
        """Close all connections in pool"""
        try:
            self.connection_pool.closeall()
            logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Failed to close database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = db_manager.get_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if connection:
            db_manager.return_connection(connection)

def execute_query(query, params=None, fetch=False):
    """Execute a query with connection management"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            
            if fetch:
                if fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'all':
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchmany(fetch)
            else:
                result = cursor.rowcount
                
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            cursor.close()

def init_database():
    """Initialize database with schema"""
    schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(schema_file):
        logger.error(f"Schema file not found: {schema_file}")
        return False
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema creation
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()
            
        logger.info("Database schema initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            logger.info(f"Database connection successful. Version: {version['version']}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the connection
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
