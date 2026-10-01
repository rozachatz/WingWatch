import test from 'node:test';
import assert from 'node:assert/strict';
import {createRadarState, applyRadarFrame} from '../static/radar_state.mjs';

const frame = (run, index, ids) => ({run_id: run, frame_index: index, targets: ids.map(track_id => ({track_id}))});

test('snapshots update existing tracks, add new tracks, and remove absent tracks', () => {
    const state = createRadarState();
    applyRadarFrame(state, frame('a', 1, [1, 2]));
    applyRadarFrame(state, frame('a', 2, [1, 3]));
    assert.deepEqual(state.tracks.map(t => t.track_id), [1, 3]);
    applyRadarFrame(state, frame('a', 3, []));
    assert.deepEqual(state.tracks, []);
});

test('duplicates and older frames leave the displayed snapshot intact', () => {
    const state = createRadarState();
    applyRadarFrame(state, frame('a', 4, [1]));
    assert.equal(applyRadarFrame(state, frame('a', 4, [2])), false);
    assert.equal(applyRadarFrame(state, frame('a', 3, [])), false);
    assert.deepEqual(state.tracks.map(t => t.track_id), [1]);
});

test('new runs reset the view and delayed frames from retired runs are ignored', () => {
    const state = createRadarState();
    applyRadarFrame(state, frame('a', 10, [1]));
    assert.equal(applyRadarFrame(state, frame('b', 1, [])), true);
    assert.equal(state.runId, 'b');
    assert.deepEqual(state.tracks, []);
    assert.equal(applyRadarFrame(state, frame('a', 11, [2])), false);
    assert.equal(state.runId, 'b');
});
