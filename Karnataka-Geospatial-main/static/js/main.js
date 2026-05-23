// State management
let currentPage = 0;
const pageSize = 50;
let selectedFeatureId = null;

// DOM Elements
const loadFeaturesBtn = document.getElementById('loadFeaturesBtn');
const featureList = document.getElementById('featureList');
const featureForm = document.getElementById('featureForm');
const featureName = document.getElementById('featureName');
const featureGeometry = document.getElementById('featureGeometry');
const saveFeatureBtn = document.getElementById('saveFeature');
const deleteFeatureBtn = document.getElementById('deleteFeature');
const searchInput = document.getElementById('searchFeatures');
const featureInfo = document.getElementById('featureInfo');

// Map Controls
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const fitBoundsBtn = document.getElementById('fitBounds');

// Initialize map centered on Karnataka
const map = L.map('map').setView([15.3173, 75.7139], 7);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: ' OpenStreetMap contributors'
}).addTo(map);

// Initialize feature layer
let featuresLayer = L.geoJSON(null, {
    style: {
        color: '#3498db',
        weight: 2,
        opacity: 0.8,
        fillOpacity: 0.35
    },
    onEachFeature: (feature, layer) => {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: showFeatureInfo
        });
    }
}).addTo(map);

// Feature styling functions
function highlightFeature(e) {
    const layer = e.target;
    layer.setStyle({
        weight: 3,
        color: '#2980b9',
        fillOpacity: 0.5
    });
}

function resetHighlight(e) {
    featuresLayer.resetStyle(e.target);
}

function showFeatureInfo(e) {
    const feature = e.target.feature;
    featureInfo.innerHTML = `
        <strong>${feature.properties.name}</strong>
        <p>${feature.properties.description || 'No description'}</p>
    `;
    featureInfo.style.display = 'block';
}

// Load features from API
async function loadFeatures(page = 0) {
    try {
        console.log(`Fetching features: page=${page}, pageSize=${pageSize}`);
        const response = await fetch(`/api/features/?limit=${pageSize}&offset=${page * pageSize}`);
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Received features:', data);
        
        // Clear existing features
        featureList.innerHTML = '';
        featuresLayer.clearLayers();

        // Populate feature list and map
        data.forEach(feature => {
            // Create feature card
            const featureCard = document.createElement('div');
            featureCard.className = 'feature-card';
            featureCard.innerHTML = `
                <h6>${feature.name}</h6>
                <small>${feature.description || 'No description'}</small>
            `;
            featureCard.addEventListener('click', () => selectFeature(feature));
            featureList.appendChild(featureCard);

            // Add to map
            const geoJsonFeature = {
                type: 'Feature',
                properties: feature,
                geometry: feature.geometry
            };
            featuresLayer.addData(geoJsonFeature);
        });

        // Fit map to features
        if (data.length > 0) {
            map.fitBounds(featuresLayer.getBounds());
        }

        currentPage = page;
    } catch (error) {
        console.error('Complete error details:', error);
        featureList.innerHTML = `
            <div class="alert alert-danger">
                Error loading features: ${error.message}
                <details>${error.stack}</details>
            </div>
        `;
    }
}

// Search functionality
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
});

// Map control functions
zoomInBtn.addEventListener('click', () => map.zoomIn());
zoomOutBtn.addEventListener('click', () => map.zoomOut());
fitBoundsBtn.addEventListener('click', () => {
    // Default Karnataka bounds
    map.fitBounds([
        [11.5, 74], 
        [18.5, 78.5]
    ]);
});

function selectFeature(feature) {
    selectedFeatureId = feature.id;
    featureName.value = feature.name;
    featureGeometry.value = JSON.stringify(feature.geometry, null, 2);
    deleteFeatureBtn.style.display = 'inline-block';
    
    // Highlight selected feature
    featuresLayer.eachLayer(layer => {
        if (layer.feature.properties.id === feature.id) {
            layer.setStyle({
                color: '#e74c3c',
                weight: 4
            });
        } else {
            featuresLayer.resetStyle(layer);
        }
    });
}

async function handleFeatureSubmit(e) {
    e.preventDefault();
    try {
        const method = selectedFeatureId ? 'PUT' : 'POST';
        const url = selectedFeatureId 
            ? `/api/features/${selectedFeatureId}` 
            : '/api/features/';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: featureName.value,
                geometry: JSON.parse(featureGeometry.value)
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save feature');
        }

        loadFeatures(currentPage);
        clearForm();
    } catch (error) {
        console.error('Error saving feature:', error);
        alert(`Error: ${error.message}`);
    }
}

async function handleFeatureDelete() {
    if (!selectedFeatureId) return;

    try {
        const response = await fetch(`/api/features/${selectedFeatureId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete feature');
        }

        loadFeatures(currentPage);
        clearForm();
    } catch (error) {
        console.error('Error deleting feature:', error);
        alert(`Error: ${error.message}`);
    }
}

function clearForm() {
    selectedFeatureId = null;
    featureName.value = '';
    featureGeometry.value = '';
    deleteFeatureBtn.style.display = 'none';
    
    // Reset feature styles
    featuresLayer.eachLayer(layer => {
        featuresLayer.resetStyle(layer);
    });
}

// Event Listeners
saveFeatureBtn.addEventListener('click', handleFeatureSubmit);
deleteFeatureBtn.addEventListener('click', handleFeatureDelete);
loadFeaturesBtn.addEventListener('click', () => loadFeatures(currentPage));

// Initialize
loadFeatures();
