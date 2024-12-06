const API = {
    baseUrl: 'http://localhost:8000',

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