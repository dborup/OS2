// Works with everything we wanted Sunday
// Custom icons for each severity level
var customIcons = {
    'Critical': new L.Icon({
        iconUrl: 'static/red-icon.png', // Path to your red icon
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
    }),
    'High': new L.Icon({
        iconUrl: 'static/orange-icon.png', // Path to your orange icon
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
    }),
    'Normal': new L.Icon({
        iconUrl: 'static/green-icon.png', // Path to your green icon
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
    })
};

// Initialize the Leaflet map centered on Aarhus, Denmark
var cityMap = L.map('city-map').setView([56.1629, 10.2039], 19);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(cityMap);

// Function to process data and organize by severity and monitoring rule
function processEventData(data) {
    let locationData = {};

    data.forEach(location => {
        const locationKey = `${location.latitude}_${location.longitude}`;
        let highestSeverity = "Normal"; // Default severity
        let ruleGroups = {};

        location.events.forEach(event => {
            // Update highest severity
            if (event.level === 'Critical' || (event.level === 'High' && highestSeverity !== 'Critical')) {
                highestSeverity = event.level;
            }

            // Group by monitoring rule
            const ruleKey = event.monitoring_rule;
            if (!ruleGroups[ruleKey]) {
                ruleGroups[ruleKey] = new Set();
            }

            let eventEntry = event.pc_name;
            if (event.level === 'High' || event.level === 'Critical') {
                eventEntry += ` (Summary: ${event.event_summary})`;
            }
            ruleGroups[ruleKey].add(eventEntry);
        });

        locationData[locationKey] = {
            level: highestSeverity,
            ruleGroups: ruleGroups
        };
    });

    return locationData;
}

// Function to update the markers on the map
function updateCityMapMarkers() {
    fetch('/api/filtered_computer_events')
        .then(response => response.json())
        .then(data => {
            cityMap.eachLayer(layer => {
                if (!!layer.toGeoJSON) cityMap.removeLayer(layer);
            });

            const processedData = processEventData(data);

            Object.entries(processedData).forEach(([locationKey, locationInfo]) => {
                const [latitude, longitude] = locationKey.split('_');
                const icon = customIcons[locationInfo.level] || new L.Icon.Default();

                let popupContent = '';
                Object.keys(locationInfo.ruleGroups).forEach(rule => {
                    let eventDetails = Array.from(locationInfo.ruleGroups[rule]).join('<br>');
                    popupContent += `<strong>${rule}</strong>:<br>${eventDetails}<br><hr>`;
                });

                L.marker([parseFloat(latitude), parseFloat(longitude)], { icon: icon })
                    .addTo(cityMap)
                    .bindPopup(popupContent, { maxHeight: 200 });
            });
        })
        .catch(error => console.error('Error:', error));
}

updateCityMapMarkers();
setInterval(updateCityMapMarkers, 60000); // Update every 60 seconds
