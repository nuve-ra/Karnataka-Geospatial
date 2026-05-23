const API = {
    baseUrl: 'http://localhost:8000',

    // Fetch a list of features with pagination support (limit and offset)
    async getFeatures(limit = 50, offset = 0) {
        try {
            const response = await fetch(`${this.baseUrl}/features?limit=${limit}&offset=${offset}`);
            if (!response.ok) throw new Error('Failed to fetch features');
            return await response.json();
        } catch (error) {
            console.error('Error fetching features:', error);
            throw error;
        }
    },

    // Fetch a single feature by its ID
    async getFeature(id) {
        try {
            const response = await fetch(`${this.baseUrl}/features/${id}`);
            if (!response.ok) throw new Error('Failed to fetch feature');
            return await response.json();
        } catch (error) {
            console.error('Error fetching feature:', error);
            throw error;
        }
    },

    // Create a new feature
    async createFeature(feature) {
        try {
            const response = await fetch(`${this.baseUrl}/features`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feature)
            });
            if (!response.ok) throw new Error('Failed to create feature');
            return await response.json();
        } catch (error) {
            console.error('Error creating feature:', error);
            throw error;
        }
    },

    // Update an existing feature by its ID
    async updateFeature(id, feature) {
        try {
            const response = await fetch(`${this.baseUrl}/features/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feature)
            });
            if (!response.ok) throw new Error('Failed to update feature');
            return await response.json();
        } catch (error) {
            console.error('Error updating feature:', error);
            throw error;
        }
    },

    // Delete a feature by its ID
    async deleteFeature(id) {
        try {
            const response = await fetch(`${this.baseUrl}/features/${id}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete feature');
            return await response.json();
        } catch (error) {
            console.error('Error deleting feature:', error);
            throw error;
        }
    }
};

// Example Usage

// Fetching features
async function loadFeatures() {
    try {
        const features = await API.getFeatures(10, 0);  // Fetch first 10 features
        console.log(features);
    } catch (error) {
        console.error('Failed to load features:', error);
    }
}

// Creating a new feature
const newFeature = {
    name: 'New Feature',
    description: 'A description of the new feature',
    location: 'Some Location'
};

async function createNewFeature() {
    try {
        const createdFeature = await API.createFeature(newFeature);
        console.log('Created Feature:', createdFeature);
    } catch (error) {
        console.error('Failed to create feature:', error);
    }
}

// Updating a feature
const updatedFeature = {
    name: 'Updated Feature',
    description: 'Updated description',
    location: 'Updated Location'
};

async function updateExistingFeature(id) {
    try {
        const updated = await API.updateFeature(id, updatedFeature);
        console.log('Updated Feature:', updated);
    } catch (error) {
        console.error('Failed to update feature:', error);
    }
}

// Deleting a feature
async function deleteFeature(id) {
    try {
        const deletedFeature = await API.deleteFeature(id);
        console.log('Deleted Feature:', deletedFeature);
    } catch (error) {
        console.error('Failed to delete feature:', error);
    }
}
