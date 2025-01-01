from datetime import datetime
from db_utils import fetch_from_db
import logging

logger = logging.getLogger(__name__)

def validate_license(client_id, license_key):
    """
    Validate a license using the database.
    """
    try:
        query = """
            SELECT license_key, status, expires_at
            FROM Licenses
            WHERE client_id = %s
        """
        result = fetch_from_db(query, (client_id,))

        if not result:
            logger.warning(f"No license found for client_id: {client_id}")
            return {"valid": False, "reason": "License not found"}

        license_info = result[0]
        # Check if the license_key matches
        if license_info['license_key'] != license_key:
            return {"valid": False, "reason": "Invalid license key"}

        # Check if status is 'active'
        if license_info['status'].lower() != 'active':
            return {"valid": False, "reason": f"License {license_info['status'].lower()}"}

        # Now handle expires_at
        expires_at_val = license_info['expires_at']

        # If the DB driver already returns a datetime, compare directly
        if isinstance(expires_at_val, datetime):
            expires_at = expires_at_val
        # Else assume it's a string; parse accordingly
        elif isinstance(expires_at_val, str):
            try:
                # If it's proper ISO-8601, fromisoformat() will work:
                expires_at = datetime.fromisoformat(expires_at_val)
            except ValueError:
                # If it's a different format (e.g. "YYYY-MM-DD HH:MM:SS"), use strptime
                expires_at = datetime.strptime(expires_at_val, "%Y-%m-%d %H:%M:%S")
        else:
            logger.error(f"Unexpected expires_at type: {type(expires_at_val)}")
            return {"valid": False, "reason": "Validation error"}

        # Check for expiration
        if expires_at < datetime.utcnow():
            return {"valid": False, "reason": "License expired"}

        return {"valid": True}
    except Exception as e:
        logger.error(f"Error validating license: {e}")
        return {"valid": False, "reason": "Validation error"} 