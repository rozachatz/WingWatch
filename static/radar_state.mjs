// Complete snapshots replace current tracks. No history is retained.
export function createRadarState() {
    return {runId: null, frameIndex: -1, tracks: [], retiredRunIds: new Set()};
}

export function applyRadarFrame(state, frame) {
    if (state.retiredRunIds.has(frame.run_id)) return false;
    if (frame.run_id === state.runId && frame.frame_index <= state.frameIndex) return false;
    if (state.runId !== null && frame.run_id !== state.runId) {
        state.retiredRunIds.add(state.runId);
    }
    state.runId = frame.run_id;
    state.frameIndex = frame.frame_index;
    state.tracks = frame.targets;
    return true;
}
