import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import json
import os

# Configure logger
logger = logging.getLogger(__name__)

# Load environment
ENVIRONMENT = os.getenv("ENV", "development")  # Default to 'development'

# Load database configuration
CONFIG_PATH = "db_config.json"
try:
    with open(CONFIG_PATH, "r") as config_file:
        all_db_configs = json.load(config_file)
        if ENVIRONMENT not in all_db_configs:
            raise ValueError(f"Environment '{ENVIRONMENT}' not found in configuration.")
        db_config = all_db_configs[ENVIRONMENT]
        logger.info(f"Database configuration loaded for environment: {ENVIRONMENT}")
except FileNotFoundError:
    logger.error("Database configuration file not found.")
    raise
except json.JSONDecodeError:
    logger.error("Error decoding database configuration file.")
    raise
except Exception as e:
    logger.error(f"Error loading database configuration: {e}")
    raise


def get_db_connection():
    """
    Establishes and returns a database connection.
    """
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config.get("password", ""),
            port=db_config.get("port", 5432),
            sslmode=db_config.get("sslmode", "disable")
        )
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


def fetch_from_db(query, params=None):
    """
    Executes a query and fetches results.
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        conn.close()
        logger.debug(f"Query executed successfully: {query}")
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


def execute_query(query, params=None):
    """
    Executes a SQL query with optional parameters.
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            conn.commit()
            logger.info("Query executed successfully.")
        conn.close()
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise RuntimeError("Database query execution failed.")