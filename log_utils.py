from db_utils import execute_query
import logging

logger = logging.getLogger(__name__)

def save_log_to_db(log_data):
    """
    Save log data to the database with error handling for missing keys and invalid types.
    Handles nested fields like 'machine_specs'.
    """
    try:
        # Extract nested fields from 'machine_specs'
        machine_specs = log_data.get("machine_specs", {})
        log_data["os"] = machine_specs.get("os", "Unknown")
        log_data["os_version"] = machine_specs.get("os_version", "Unknown")
        log_data["machine"] = machine_specs.get("machine", "Unknown")

        # List of required keys
        required_keys = [
            "ip", "machine_name", "os", "os_version", "machine",
            "start_time", "end_time", "file_size", "video_length",
            "processing_time", "type", "function_type", "status", "error_logs"
        ]

        # Validate for missing or None keys
        for key in required_keys:
            if key not in log_data:
                logger.error(f"Missing required log field: {key}")
                raise ValueError(f"Missing required log field: {key}")
            if log_data[key] is None:
                logger.warning(f"Log field '{key}' is None. Defaulting to empty or zero.")
                log_data[key] = "" if isinstance(log_data[key], str) else 0

        # Debugging log data before insertion
        logger.debug(f"Prepared log data for DB insertion: {log_data}")

        # SQL query for inserting log data
        query = """
            INSERT INTO Logs (
                ip, machine_name, os, os_version, machine,
                start_time, end_time, file_size, video_length,
                processing_time, type, function_type, status, error_logs
            ) VALUES (
                %(ip)s, %(machine_name)s, %(os)s, %(os_version)s, %(machine)s,
                %(start_time)s, %(end_time)s, %(file_size)s, %(video_length)s,
                %(processing_time)s, %(type)s, %(function_type)s, %(status)s, %(error_logs)s
            )
        """
        execute_query(query, log_data)
        logger.info("Log successfully saved to the database.")

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise
    except KeyError as ke:
        logger.error(f"Key error while saving log: {ke}")
        raise RuntimeError("Log data is missing required fields.")
    except Exception as e:
        logger.error(f"Unexpected error saving log to database: {e}")
        raise RuntimeError("Failed to save log to database.")