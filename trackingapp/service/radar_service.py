"""One replay clock for both synthetic fixtures and Malaxa-exported files."""
import asyncio
import math
from pathlib import Path
from uuid import uuid4

from trackingapp.service.frame_replay_source import load_adsb, load_frames

DEFAULT_FRAMES = Path(__file__).parents[2]/'fixtures/radar-demo'


class RadarService:
    source = 'files'

    def __init__(self, interval_seconds: float = 1.0, directory: Path | None = None):
        if not math.isfinite(interval_seconds) or interval_seconds < 0:
            raise ValueError('replay timing multiplier must be finite and nonnegative')
        self.interval_seconds = interval_seconds
        directory = directory if directory is not None else DEFAULT_FRAMES
        self.frames = load_frames(directory)
        self.adsb_frames = load_adsb(directory, self.frames)
        self.latest = None
        self.paused = True
        self._task = None

    async def restart(self):
        await self.stop()
        self.run_id = f'replay-{uuid4()}'
        self.latest = self.frames[0].model_copy(update={'run_id': self.run_id})
        self.paused = len(self.frames) == 1
        self._task = asyncio.create_task(self._replay())
        return self.latest

    async def _replay(self):
        for previous, frame in zip(self.frames, self.frames[1:]):
            delay = (frame.timestamp-previous.timestamp).total_seconds()*self.interval_seconds
            await asyncio.sleep(delay)
            self.latest = frame.model_copy(update={'run_id': self.run_id})
        self.paused = True

    async def stop(self):
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self.paused = True

    def current_aircraft(self) -> list:
        if self.latest is None:
            return []
        snapshot = self.adsb_frames.get(self.latest.frame_index)
        return snapshot.aircraft if snapshot else []
