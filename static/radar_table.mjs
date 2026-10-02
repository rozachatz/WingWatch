import {applyRadarFrame, createRadarState} from './radar_state.mjs';

const state = createRadarState();
const rows = document.getElementById('radar-rows');
const summary = document.getElementById('radar-summary');
const connection = document.getElementById('radar-connection');
const restartButton = document.getElementById('radar-restart');
let generation = 0;
let selectedTrackId = null;
let contourGeneration = 0;
const contourNote = document.getElementById('radar-contour-note');

function clearContour() {
    contourGeneration += 1;
    window.dispatchEvent(new CustomEvent('radar-contour', {detail: null}));
}

async function updateContour() {
    clearContour();
    if (selectedTrackId === null) {
        contourNote.textContent = 'Select a radar track to show its possible-location contour.';
        return;
    }
    const token = contourGeneration;
    contourNote.textContent = `Track ${selectedTrackId} · calculating contour…`;
    const query = new URLSearchParams({run_id: state.runId, frame_index: state.frameIndex});
    try {
        const contour = await requestJson(`/api/v1/tracks/${selectedTrackId}/contour?${query}`);
        if (token !== contourGeneration) return;
        window.dispatchEvent(new CustomEvent('radar-contour', {detail: contour}));
        contourNote.textContent = `Track ${selectedTrackId} · assumed altitude: 1,000 m (WGS84 ellipsoid) · possible locations, not an aircraft position`;
    } catch {
        if (token === contourGeneration) contourNote.textContent = 'Contour unavailable for this snapshot; retrying on the next poll.';
    }
}

function selectTrack(trackId) {
    selectedTrackId = trackId;
    for (const row of rows.children) {
        row.classList.toggle('radar-selected', Number(row.dataset.trackId) === trackId);
        const button = row.querySelector('button');
        if (button) button.setAttribute('aria-pressed', String(Number(row.dataset.trackId) === trackId));
    }
    updateContour();
}
let pollInProgress = false;
let restartInProgress = false;

async function requestJson(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    try {
        const response = await fetch(url, {...options, signal: controller.signal, cache: 'no-store'});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } finally {
        clearTimeout(timeout);
    }
}

function render(frame) {
    const previousRunId = state.runId;
    if (!applyRadarFrame(state, frame)) {
        if (selectedTrackId !== null && contourNote.textContent.startsWith('Contour unavailable')) updateContour();
        return;
    }
    if (previousRunId !== state.runId || !state.tracks.some(t => t.track_id === selectedTrackId)) {
        selectedTrackId = null;
    }
    window.dispatchEvent(new CustomEvent('radar-frame', {detail: frame}));
    document.getElementById("radar-source-note").textContent = frame.localization.note;
    rows.replaceChildren();
    if (state.tracks.length === 0) {
        const cell = document.createElement('td');
        cell.colSpan = 5;
        cell.textContent = 'No active radar tracks';
        const row = document.createElement('tr');
        row.append(cell);
        rows.append(row);
    }
    for (const track of state.tracks) {
        const row = document.createElement('tr');
        for (const value of [track.track_id, track.status,
            track.bistatic_range_m.toFixed(1), track.doppler_hz.toFixed(2), track.misses]) {
            const cell = document.createElement('td');
            cell.textContent = value;
            row.append(cell);
        }
        row.dataset.trackId = track.track_id;
        const selectButton = document.createElement('button');
        selectButton.type = 'button';
        selectButton.textContent = `Track ${track.track_id}`;
        selectButton.setAttribute('aria-pressed', String(track.track_id === selectedTrackId));
        selectButton.addEventListener('click', () => selectTrack(track.track_id));
        row.children[0].replaceChildren(selectButton);
        row.classList.toggle('radar-selected', track.track_id === selectedTrackId);
        row.children[1].className = `radar-status-${track.status}`;
        rows.append(row);
    }
    updateContour();
    summary.textContent = `${frame.mode === 'replay' ? 'Replay' : 'Live'} · frame ${frame.frame_index}`;
}

async function poll() {
    if (pollInProgress || restartInProgress) return;
    pollInProgress = true;
    const requestedGeneration = generation;
    try {
        const frame = await requestJson('/api/v1/frames/latest');
        if (requestedGeneration !== generation) return;
        render(frame);
        connection.textContent = 'Connected';
        // Paused is distinct from disconnected; duplicates still refresh source health.
        try {
            const status = await requestJson('/api/v1/status');
            if (requestedGeneration !== generation) return;
            if (status.run_id === state.runId && status.latest_frame_index === state.frameIndex) {
                connection.textContent = status.source_connected
                    ? status.paused ? 'Replay finished · press Restart replay' : 'Connected · playing'
                    : 'Source disconnected · showing last snapshot';
            }
        } catch {
            if (requestedGeneration === generation) connection.textContent = 'Connected · replay status unavailable';
        }
    } catch {
        if (requestedGeneration === generation) {
            connection.textContent = state.runId === null
                ? 'Disconnected · waiting for radar' : 'Disconnected · showing last snapshot';
        }
    } finally {
        pollInProgress = false;
    }
}

restartButton.addEventListener('click', async () => {
    restartInProgress = true;
    restartButton.disabled = true;
    generation += 1; // Ignore any response requested before restart.
    clearContour();
    try {
        render(await requestJson('/api/v1/replay/restart', {method: 'POST'}));
        connection.textContent = 'Connected';
    } catch {
        connection.textContent = 'Restart failed · last snapshot retained; polling will retry';
    } finally {
        restartInProgress = false;
        restartButton.disabled = false;
    }
});

poll();
setInterval(poll, 1000);
