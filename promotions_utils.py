from db_utils import fetch_from_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_promotions():
    """
    Fetch active promotions from the database.
    """
    try:
        query = """
            SELECT message, start_time, end_time
            FROM Promotions
            WHERE start_time <= %s AND end_time >= %s
        """
        now = datetime.utcnow()
        results = fetch_from_db(query, (now, now))

        promotions = []
        for promo in results:
            try:
                # Ensure that start_time and end_time are valid
                start_time = promo.get("start_time")
                end_time = promo.get("end_time")

                # Parse start_time and end_time if they're strings
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)

                # Add the promotion message if valid
                if start_time <= now <= end_time:
                    promotions.append(promo["message"])
                else:
                    logger.warning(f"Skipped promotion outside active period: {promo}")
            except Exception as promo_error:
                logger.error(f"Error processing promotion: {promo}. Error: {promo_error}")

        return promotions
    except Exception as e:
        logger.error(f"Error fetching promotions: {e}")
        return []