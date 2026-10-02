# WingWatch

WingWatch displays ADS-B aircraft and passive-radar tracks and supports antenna
pointing through Hamlib. Radar replay can run without radio or rotator hardware.

## Hardware-free radar replay

Python 3.10+ is required. From the repository directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-demo.txt
uvicorn trackingapp.main:trackingapp --reload
```

Open http://127.0.0.1:8000. Click **Restart replay**, then **Track 1** when it
appears to see the contour and moving Demo ADS-B marker. Click the blue demo
aircraft and **Track demo aircraft**, or click **Track demo ADS-B** below the
map, to show simulated rotator azimuth, elevation, and a short direction line
from the receiver. The demo finishes after
ten seconds; restart to watch it again. API documentation is at `/docs`.

The default source is the bundled synthetic JSON
fixture in `fixtures/radar-demo/`. One replay service handles these fixtures and
Malaxa-exported frames. There is no separate runtime simulator.

The demo has ten one-second frames: empty; tentative in 2–3; confirmed in 4–6;
coasting in 7–9; removed in 10. Restart replay starts the files again with a new
session run_id. Original measurement timestamps and indexes are preserved.
Replay pauses after the final frame and remains connected. No history database
is used; loaded files and current state are held in memory. Use one server worker.

The table shows active track ID, status, bistatic range, Doppler, and misses.
Snapshots replace the active table; duplicates/older frames are ignored. New
sessions clear selection. A failed poll retains the last snapshot and labels it
disconnected. The browser polls once per second and can skip intermediate frames.

The map shows receiver/transmitter sites. Select a track to show one range
contour using an assumed 1,000 m WGS84 ellipsoidal altitude. The contour updates
and disappears with the selected track. Its colour follows status; coasting is
dashed. It represents possible locations, not an aircraft position. The local
solver supports ranges and site baselines up to 100 km, requires its midpoint
inside the contour, and rejects unsupported geometry. Real localization remains
unresolved. Basemap tiles and Leaflet require internet access; the table works
independently of map scripts.

## Replay Malaxa exports

Malaxa owns the authoritative run config and converts its modern native tracker
files into RadarFrame v2. Point the same WingWatch service at its output:

```sh
WINGWATCH_RADAR_FRAMES=/absolute/path/to/wingwatch-frames-new-session \
uvicorn trackingapp.main:trackingapp --reload
```

The loader reads only `frame_*.json`, validates JSON Schema and models before
startup, and rejects empty sources, mixed runs, duplicate indexes, v1 frames,
non-finite measurements, and non-increasing timestamps. Files are loaded once,
not watched. Frames advance at their recorded timestamp spacing. Restart creates
a fresh UI session identity while preserving capture times and measurements.
Metadata comes from the frames; WingWatch needs no duplicate processing config.
The UI displays the source's localization note, including whether it is synthetic
or the site metadata is unverified.

## Fixture generation

The ten-frame scenario is now a development fixture generator. It does not run
as part of the application. Generate another set in an empty directory:

```sh
python -m trackingapp.demo_fixture_generator --output local-data/new-demo-fixture
```

The bundled fixture has an explicit synthetic epoch, site hypotheses, physically
consistent range/Doppler, null geographic positions, and unavailable confidence.
Its excess range uses its demo site baseline. Actual Malaxa exports use the
baseline saved from radar processing instead.

## API and contract

- `GET /api/v1/frames/latest`: current complete RadarFrame v2.
- `GET /api/v1/status`: typed source/replay state, latest frame and paused state.
- `POST /api/v1/replay/restart`: restart the loaded files with a new session ID.
- `GET /api/v1/tracks/{track_id}/contour?run_id=...&frame_index=...`: GeoJSON contour.

Contour requests return 409 when the snapshot changed and 404 for a missing
track. The browser ignores obsolete contour responses. Confidence can be null;
confirmed tracks with misses map to coasting, while tentative tracks stay
tentative. The current WingWatch model requires numeric frequency. The shared
v2 schema still allows that field to be omitted. ADS-B data is a separate source.
WebSocket delivery, live radar ingestion, and historical frame endpoints are
not implemented.

## Checks

```sh
pip install -r requirements-demo-dev.txt
python -m pytest tests/test_radar_demo.py tests/test_range_contour.py tests/test_frame_replay.py tests/test_adsb_replay.py -q
node --test tests/test_radar_state.mjs
```

## Existing ADS-B and hardware mode

Install `requirements.txt`, configure `LATITUDE`, `LONGITUDE`, and `ALTITUDE`,
and start the existing dump1090/Hamlib services through Docker Compose. Launch:

```sh
WINGWATCH_MODE=hardware uvicorn trackingapp.main:trackingapp --reload
```

`/api/aircraft` and aircraft selection retain the existing ADS-B path. Hardware
integration code has not yet had the planned cleanup or hardware revalidation.

## Demo ADS-B companion file

`trackingapp/models/adsb_models.py` defines the demo `adsb.json` file contract.
The bundled fixture includes one synthetic aircraft, ICAO abc001 / DEMO01,
with positions at 1,000 m WGS84 ellipsoidal altitude. Radar measurements
and ADS-B reports derive from the same constructed trajectory. Reports share
radar measurement timestamps and advance/restart on the same replay clock.
The aircraft marker is explicitly labelled Demo ADS-B, and the radar contour
remains a possible-location contour. No automatic association is implemented.
The simulated rotator follows only the aircraft selected by ICAO ID; its arrow indicates commanded direction, not
physical motion or measured antenna feedback.

Radar misses and deletion do not delete the ADS-B aircraft: it is still present
in the companion reports. Radar `position` stays null. The generated reports are
fixture truth, not evidence of actual radar detection accuracy.

For a directory without adsb.json, demo-mode `/api/aircraft` returns an empty
list. If provided, the companion must cover every loaded radar frame (empty
aircraft snapshots are allowed), use matching timestamps, and contain no duplicate
indexes/aircraft. Only demo ADS-B reports are supported by this companion format
for now. Real dump1090 reception remains the separate hardware-mode path: it
returns its existing ADS-B dictionaries and is not validated by the demo model.
Before sharing one model with the live feed, its altitude units and reference
datum must be verified and normalized.

`GET /api/v1/pointing?run_id=...&frame_index=...` returns the simulated
command for the current demo snapshot; stale requests return 409. Selection
uses the existing `POST /api/select_aircraft/{hex_id}` route in demo mode.
Replay restart clears selection and recorded commands. Demo pointing calls the
same `RotatorConfigureService` as hardware mode, using a simulated client that
records its commands. Hardware mode sends the command to Hamlib. Neither mode
provides measured antenna orientation feedback.

`GET /api/aircraft?run_id=...&frame_index=...` requests the current matching
snapshot in demo mode; an outdated identity returns 409. This avoids displaying
a newer ADS-B sample beside an older radar frame. Existing clients can still call
`GET /api/aircraft` without parameters. Altitude in companion reports is metres.

```sh
python -m pytest tests/test_adsb_replay.py -q
```

## Project structure

| File or directory | Responsibility |
| --- | --- |
| `trackingapp/main.py` | Create the app, configure services/lifecycle, mount static files and include routers |
| `trackingapp/api/radar.py` | Radar frames, status, replay restart and contours |
| `trackingapp/api/aircraft.py` | ADS-B reports and aircraft selection |
| `trackingapp/service/` | Replay, geometry, ADS-B tracking and hardware/demo pointing logic |
| `trackingapp/dao/simulated_rotator_client.py` | Record demo antenna commands without opening a socket |
| `trackingapp/models/` | Radar and demo ADS-B contracts, plus simulated pointing status |
| `static/map.html` | Page markup |
| `static/map.css` | Map, table and popup styles |
| `static/map.js` | Map layers, aircraft markers, contours and popups |
| `static/radar_table.mjs` | Radar polling, table, selection and restart |
| `static/radar_state.mjs` | Complete-snapshot state rules |
| `fixtures/radar-demo/` | Small version-controlled radar and ADS-B demo inputs |
| `local-data/` | Ignored local recordings, exported runs and fixture experiments |

Run commands from the WingWatch repository root, using the activated virtual
environment. Keep real recordings and generated exports under `local-data/` or
outside the repository. Python caches, virtual environments, editor files, and
local `.env` settings are ignored; the bundled demo JSON files remain reviewable.

Altitude normalization, negative-elevation behaviour, broader hardware/feed
reliability, and dependency refactoring are deferred beyond the display MVP.
