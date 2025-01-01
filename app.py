from flask import Flask, request, jsonify
from license_utils import validate_license
from promotions_utils import fetch_promotions
from log_utils import save_log_to_db
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

def parse_request_data():
    """
    Parse JSON data from the request, even if Content-Type is not set.
    """
    try:
        if request.content_type != "application/json":
            logger.warning("Content-Type not set or not application/json, assuming JSON payload.")
        data = request.get_json(force=True)  # Silent mode prevents Flask from throwing errors
        if data is None:
            raise ValueError("Unable to parse JSON. Ensure the request body is valid JSON.")
        return data
    except Exception as e:
        logger.error(f"Error parsing request data: {e}")
        raise ValueError("Invalid JSON format in request body.")


@app.route('/validate', methods=['POST'])
def validate():
    """
    Endpoint to validate a license.
    """
    try:
        data = parse_request_data()
        logger.debug(f"License validation request: {data}")

        # Validate required fields
        if not data or 'client_id' not in data or 'license_key' not in data:
            return jsonify({"error": "Invalid request. 'client_id' and 'license_key' are required."}), 400

        client_id = data['client_id']
        license_key = data['license_key']
        validation_result = validate_license(client_id, license_key)

        if not validation_result['valid']:
            logger.warning(f"License validation failed: {validation_result['reason']}")
            return jsonify({"error": validation_result['reason']}), 403

        logger.info(f"License validated successfully for client_id: {client_id}")
        return jsonify({"message": "License validation successful"}), 200
    except Exception as e:
        logger.error(f"Error during license validation: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/promotions', methods=['POST'])
def promotions():
    """
    Endpoint to fetch active promotions.
    """
    try:
        data = parse_request_data()
        logger.debug(f"Promotions request: {data}")

        if not data or 'client_id' not in data:
            return jsonify({"error": "Invalid request. 'client_id' is required."}), 400

        client_id = data['client_id']
        promotions = fetch_promotions()

        logger.info(f"Promotions fetched for client_id: {client_id}")
        return jsonify({"promotions": promotions}), 200
    except Exception as e:
        logger.error(f"Error fetching promotions: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/log', methods=['POST'])
def log():
    """
    Endpoint to log data.
    """
    try:
        data = parse_request_data()
        logger.info(f"Log data received: {data}")

        # Save log data to the database
        save_log_to_db(data)

        return jsonify({"message": "Log processed and saved successfully"}), 200
    except ValueError as ve:
        logger.error(f"Invalid log data: {ve}")
        return jsonify({"error": "Invalid log data"}), 400
    except Exception as e:
        logger.error(f"Error processing log: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5175, debug=True)