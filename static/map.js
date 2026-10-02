(() => {
    // Initialize the Leaflet map
    const map = L.map('map').setView([38.0, 23.0], 6); // Center at specified coordinates
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, // Maximum zoom level
    }).addTo(map); // Add tile layer to the map

    let latestRadarSnapshot = null;
    let aircraftTrail = null;
    let aircraftTrailPoints = [];
    let radarSites = null;
    let rangeContour = null;
    let focusedContourKey = null;
    let radarMapRunId = null;
    let pointingLayer = null;
    let pointingRequest = 0;
    const pointingStatus = document.getElementById('pointing-status');
    const demoTrackButton = document.getElementById('demo-track-aircraft');

    function clearPointing() {
        if (pointingLayer) map.removeLayer(pointingLayer);
        pointingLayer = null;
    }

    async function updatePointing(frame) {
        const requestNumber = ++pointingRequest;
        clearPointing();
        const query = new URLSearchParams({run_id: frame.run_id, frame_index: frame.frame_index});
        try {
            const response = await fetch(`/api/v1/pointing?${query}`, {cache: 'no-store'});
            if (response.status === 409) return;
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const command = await response.json();
            if (requestNumber !== pointingRequest || latestRadarSnapshot !== frame) return;
            if (command.status === 'idle') {
                pointingStatus.textContent = 'Simulated rotator: select a Demo ADS-B aircraft to show pointing.';
                return;
            }
            if (command.status === 'no_report') {
                pointingStatus.textContent = `Simulated rotator: no report for ${command.selected_hex} in this frame.`;
                return;
            }
            const azimuth = command.command_azimuth_deg;
            const elevation = command.command_elevation_deg;
            pointingStatus.textContent = `Simulated rotator → ${command.selected_flight}: azimuth ${azimuth.toFixed(1)}°, elevation ${elevation.toFixed(1)}° · commanded direction`;
            const lat = command.receiver.latitude;
            const lon = command.receiver.longitude;
            const bearing = azimuth * Math.PI / 180;
            // Short line shows heading only; its length is not aircraft distance.
            const tip = [lat + 2 / 111 * Math.cos(bearing),
                         lon + 2 / (111 * Math.cos(lat * Math.PI / 180)) * Math.sin(bearing)];
            pointingLayer = L.polyline([[lat, lon], tip],
                {color: '#663399', weight: 4, dashArray: '5 4'}).addTo(map)
                .bindTooltip('Simulated rotator direction');
        } catch {
            if (requestNumber === pointingRequest) {
                pointingStatus.textContent = 'Simulated rotator: pointing data unavailable.';
            }
        }
    }
    window.addEventListener('radar-frame', ({detail: frame}) => {
        latestRadarSnapshot = frame;
        // Hide older demo reports until the matching snapshot arrives.
        for (const [hex, marker] of Object.entries(markers)) {
            if (marker.isDemoAdsB) { map.removeLayer(marker); delete markers[hex]; }
        }
        updateMap();
        updatePointing(frame);
        if (radarSites) map.removeLayer(radarSites);
        radarSites = L.layerGroup().addTo(map);
        for (const [label, site] of [['Receiver', frame.receiver], ['Transmitter', frame.transmitter]]) {
            L.circleMarker([site.latitude, site.longitude], {radius: 6, color: '#263746'})
                .bindTooltip(label, {permanent: true, direction: 'right'}).addTo(radarSites);
        }
        if (radarMapRunId !== frame.run_id) {
            radarMapRunId = frame.run_id;
            focusedContourKey = null;
            aircraftTrailPoints = [];
            if (aircraftTrail) { map.removeLayer(aircraftTrail); aircraftTrail = null; }
            map.fitBounds([[frame.receiver.latitude, frame.receiver.longitude],
                           [frame.transmitter.latitude, frame.transmitter.longitude]], {padding: [65, 65], maxZoom: 12});
        }
    });
    window.addEventListener('radar-contour', ({detail: contour}) => {
        if (rangeContour) map.removeLayer(rangeContour);
        rangeContour = null;
        if (!contour) return;
        const status = contour.properties.status;
        const color = status === 'tentative' ? '#9a5900' : status === 'confirmed' ? '#18754d' : '#59636d';
        rangeContour = L.geoJSON(contour, {style: {color, weight: 2, fillOpacity: 0.06,
            dashArray: status === 'coasting' ? '6 5' : null}})
            .bindTooltip(`Track ${contour.properties.track_id} · assumed altitude 1,000 m`).addTo(map);
        const key = `${contour.properties.run_id}:${contour.properties.track_id}`;
        if (focusedContourKey !== key) {
            focusedContourKey = key;
            map.fitBounds(rangeContour.getBounds(), {padding: [28, 28], maxZoom: 14});
        }
    });

    const airplaneIcon = L.icon({
        iconUrl: '/static/images/pin.png', // Ensure this path is correct
        iconSize: [32, 32], // Size of the icon
        iconAnchor: [16, 32], // Point of the icon which will correspond to marker's location
        popupAnchor: [0, -40] // Position the popup above the icon
    });

    let aircraftPollInProgress = false;
    let markers = {}; // Object to store markers by hex ID

    // ADS-B uses a separate model and marker; no radar association is inferred.
    async function updateMap() {
        if (aircraftPollInProgress) return;
        aircraftPollInProgress = true;
        const snapshot = latestRadarSnapshot;
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 4000);
        try {
            const query = snapshot ? '?' + new URLSearchParams({run_id: snapshot.run_id,
                frame_index: snapshot.frame_index}) : '';
            const response = await fetch('/api/aircraft' + query, {signal: controller.signal, cache: 'no-store'});
            if (response.status === 409) return; // Radar advanced; next accepted frame requests its report.
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (snapshot && (snapshot.run_id !== latestRadarSnapshot.run_id ||
                snapshot.frame_index !== latestRadarSnapshot.frame_index)) return;
            for (const marker of Object.values(markers)) map.removeLayer(marker);
            markers = {};
            demoTrackButton.hidden = true;
            data.forEach(aircraft => {
                if (!Number.isFinite(aircraft.lat) || !Number.isFinite(aircraft.lon)) return;
                const demo = aircraft.source === 'demo_adsb';
                if (demo) { demoTrackButton.hidden = false; demoTrackButton.dataset.hex = aircraft.hex; }
                const label = `${demo ? 'Demo ADS-B' : 'ADS-B'} · ${aircraft.flight || aircraft.hex}`;
                const marker = demo
                    ? L.circleMarker([aircraft.lat, aircraft.lon], {radius: 7, color: '#245ba0',
                        fillColor: '#245ba0', fillOpacity: 0.8}).addTo(map)
                    : L.marker([aircraft.lat, aircraft.lon], {icon: airplaneIcon}).addTo(map);
                if (demo && snapshot) {
                    const previous = aircraftTrailPoints[aircraftTrailPoints.length - 1];
                    if (!previous || previous.frameIndex !== snapshot.frame_index) {
                        aircraftTrailPoints.push({frameIndex: snapshot.frame_index, point: [aircraft.lat, aircraft.lon]});
                        if (aircraftTrail) map.removeLayer(aircraftTrail);
                        aircraftTrail = L.polyline(aircraftTrailPoints.map(p => p.point),
                            {color: '#245ba0', weight: 2}).addTo(map);
                    }
                }
                marker.isDemoAdsB = demo;
                marker.bindTooltip(label, {permanent: demo, direction: 'right'});
                marker.on('click', () => {
                    const content = document.getElementById('popupContent');
                    content.replaceChildren();
                    const title = document.createElement('strong');
                    title.textContent = label;
                    const details = document.createElement('p');
                    details.textContent = demo
                        ? 'Synthetic aircraft from the demo trajectory. Automatic radar matching is not implemented.'
                        : `Aircraft ICAO: ${aircraft.hex}`;
                    content.append(title, details);
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.textContent = demo ? 'Track demo aircraft' : 'Track this aircraft';
                    button.addEventListener('click', () => selectAircraft(aircraft.hex, demo));
                    content.append(button);
                    document.getElementById('popupButton').style.display = 'block';
                });
                markers[aircraft.hex] = marker;
            });
            document.getElementById('adsb-connection').textContent = data.length
                ? `ADS-B: ${data.length} aircraft` : 'ADS-B: no reports';
        } catch {
            document.getElementById('adsb-connection').textContent = 'ADS-B unavailable · last markers retained';
        } finally {
            clearTimeout(timeout);
            aircraftPollInProgress = false;
            if (snapshot && latestRadarSnapshot && (snapshot.run_id !== latestRadarSnapshot.run_id ||
                snapshot.frame_index !== latestRadarSnapshot.frame_index)) queueMicrotask(updateMap);
        }
    }

    // Fetch data every 1 seconds
    setInterval(updateMap, 1000);

    // Function to select an aircraft when a link is clicked
    function selectAircraft(hex, demo) {
        fetch(`/api/select_aircraft/${hex}`, { method: 'POST' })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(() => {
                closePopup();
                if (demo && latestRadarSnapshot) updatePointing(latestRadarSnapshot);
                if (!demo) pointingStatus.textContent = 'Hardware rotator: aircraft selected; orientation feedback unavailable.';
            })
            .catch(error => {
                pointingStatus.textContent = `Aircraft selection failed: ${error.message}`;
            });
    }

    // Function to close the popup button
    function closePopup() {
        document.getElementById('popupButton').style.display = 'none'; // Hide the button
    }

    demoTrackButton.addEventListener('click', () => {
        if (demoTrackButton.dataset.hex) selectAircraft(demoTrackButton.dataset.hex, true);
    });

    // Initial map load
    updateMap(); // Call to load initial data

    document.getElementById("popup-close").addEventListener("click", (event) => {
        event.preventDefault();
        closePopup();
    });
})();
