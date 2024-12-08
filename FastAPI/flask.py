from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/features', methods=['GET'])
def get_features():
    try:
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)
        print(f"Received limit={limit}, offset={offset}")  # Debugging output

        # Assuming a database call to fetch features
        features = fetch_features_from_database(limit, offset)
        return jsonify(features)
    
    except Exception as e:
        app.logger.error(f"Error fetching features: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

def fetch_features_from_database(limit, offset):
    # Example database fetch logic (replace with your actual logic)
    try:
        # Assuming you're using an ORM like SQLAlchemy
        # query = Feature.query.limit(limit).offset(offset).all()
        # return [feature.to_dict() for feature in query]
        return [{"id": 1, "name": "Feature 1", "description": "A test feature"}]  # Dummy data
    except Exception as e:
        app.logger.error(f"Database fetch error: {e}")
        raise e

if __name__ == '__main__':
    app.run(debug=True)
