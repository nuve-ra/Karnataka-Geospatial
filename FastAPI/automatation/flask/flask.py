from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Load GeoJSON data
GEOJSON_FILE = 'karnataka.geoJSON'

def load_geojson():
    """Load GeoJSON data from file."""
    try:
        with open(GEOJSON_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"type": "FeatureCollection", "features": []}

def save_geojson(data):
    """Save GeoJSON data to file."""
    with open(GEOJSON_FILE, 'w') as file:
        json.dump(data, file)

# API Endpoints
@app.route('/geojson', methods=['GET'])
def get_geojson():
    """Read all GeoJSON features."""
    data = load_geojson()
    return jsonify(data)

@app.route('/geojson', methods=['POST'])
def add_feature():
    """Add a new feature to GeoJSON."""
    new_feature = request.json
    data = load_geojson()
    data['features'].append(new_feature)
    save_geojson(data)
    return jsonify({"message": "Feature added successfully!"}), 201

@app.route('/geojson/<int:feature_id>', methods=['PUT'])
def update_feature(feature_id):
    """Update a feature in GeoJSON."""
    updated_feature = request.json
    data = load_geojson()
    if 0 <= feature_id < len(data['features']):
        data['features'][feature_id] = updated_feature
        save_geojson(data)
        return jsonify({"message": "Feature updated successfully!"})
    return jsonify({"error": "Feature not found!"}), 404

@app.route('/geojson/<int:feature_id>', methods=['DELETE'])
def delete_feature(feature_id):
    """Delete a feature from GeoJSON."""
    data = load_geojson()
    if 0 <= feature_id < len(data['features']):
        deleted_feature = data['features'].pop(feature_id)
        save_geojson(data)
        return jsonify({"message": "Feature deleted successfully!", "feature": deleted_feature})
    return jsonify({"error": "Feature not found!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
