# Running Wide

> **This is a fork of [dkraushar/marathon-turns](https://github.com/dkraushar/marathon-turns) by
> [Dana Kraushar](https://www.linkedin.com/in/danakraushar/).** All of the method, code, design and the original
> eight-city data are Dana's work. This fork adds one race, the **California International Marathon (CIM)** in
> Sacramento, to the comparison, using the same pipeline and the same page. See [What this fork changes](#what-this-fork-changes).

**How much farther would you run in the NYC Marathon if you took every turn on the outside?**

The marathon is certified along the *shortest possible route*: tangents, hugging every corner 1 ft off the curb.
Almost nobody runs that line, which is one reason most GPS watches read more than 26.2. This project measures
the ceiling: the extra distance if you swung around the outside of every turn.

**Answer (2026 course): about +2,990 ft (0.57 mi) across 66 turns, or +3,500 ft (0.66 mi) if you run all the way
into the far corner every time.** That's a 26.78 to 26.88 mile marathon.

## The idea in one line

Run parallel to the inside line, *w* feet farther out, and a turn through angle *θ* (radians) costs *w × θ* extra
feet, however tight or gentle the corner. So the ceiling is Σ *wᵢ·|θᵢ|* over every turn.

- **Smooth arc:** *w·θ*. A 90° turn on a 60 ft street is about +94 ft.
- **Corner to corner:** *2w·tan(θ/2)*. You run into the far corner of the intersection, then turn.

## How it's built

```
pipeline/lion.py       NYC: load LION street centerlines and build a routable graph
pipeline/course.py     NYC: rebuild the course street by street, from the race-day road-closure list
pipeline/cities.py     the eight World Marathon Majors (+ CIM) and where each course guide comes from
pipeline/osm.py        other cities: download OpenStreetMap streets along the course, estimate widths
pipeline/match.py      snap a GPX course guide onto OpenStreetMap streets
pipeline/calibrate.py  fit the OSM width estimate to NYC's measured LION widths
pipeline/turns.py      detect turns, attach street widths, compute the extra distance
pipeline/export.py     write small GeoJSON/JSON files per city for the web page
web/                   Vite + MapLibre + D3 interactive page
```

### NYC (LION)
- **Course:** there's no official GeoJSON, so the course is a list of legs ("4th Ave from 92nd St to Flatbush
  Ave") routed on LION. It includes 2026's new Bronx section (E 135th → Alexander → E 141st → 3rd Ave →
  E 138th). As a check, the routed line came out at 26.23 mi before any adjustment; the start is trimmed 75 ft
  to make it exactly 42.195 km.
- **Widths:** LION `StreetWidth_Max` (curb to curb, ft), minus 1 ft off each curb. Divided roads (4th Ave,
  bridges) use one roadbed's width, since you can't cut across the median.

### The other Majors (OpenStreetMap)
- **Course:** a GPS track of a recent edition (from [goandrace.com](https://goandrace.com)) is only a guide.
  `match.py` cuts it into ~400 m pieces and finds the cheapest path on OSM streets, where a street costs more the
  farther it is from the guide, and keeps several candidate snap points per piece so a whole-course dynamic
  program can pick the consistent ones (a wrong carriageway can't strand a piece). Long OSM segments (bridges)
  get extra nodes every 100 ft, and detours longer than the guide are penalized.
- **Hairpins:** a turn over 120° only counts if the GPS guide also turns sharply there. Real turnarounds survive;
  loops forced by OSM's road layout (ramps, plazas) are dropped and reported.
- **Widths:** OSM rarely has curb-to-curb width, so: `width` tag if mapped, else
  `lanes × 8 ft + 30 ft`, fitted to LION on NYC (`calibrate.py`). Per street it's rough (±13 ft mean error), but
  it's the same rule everywhere, which is what a ranking needs. NYC run through the OSM method lands about 9%
  above its LION result.

### Turns (both)
- Simplify the line (10 ft Douglas-Peucker), measure the heading change at each vertex, and merge
  same-direction bends within 250 ft into one turn. Turns of at least 15° count as turns; smaller ones are "bends".

## Known limitations

- A ceiling, not a prediction: barricades, water stations and crowds shrink the usable width.
- Bay Ridge has three corral routes for the first ~8 miles; this uses Dahlgren Pl → 92nd St → 4th Ave.
- The Queensboro Bridge exit onto 1st Ave is probably a bigger loop in real life than LION's ramp geometry shows.
- The Madison Ave Bridge shows a small zigzag (about 60 ft of "turns") that may be a LION drawing artifact.
- OSM widths assume NYC-style street parking; cities with less of it (Tokyo especially) probably come out wide.
- Courses outside NYC are recent editions' GPS tracks, not certified course files.

## Run it

```bash
# Python pipeline (Python 3.12, uv). LION 26C from NYC Planning goes in data/raw/lion/.
curl -L -o data/raw/lion/nyclion_26c.zip https://s-media.nyc.gov/agencies/dcp/assets/files/zip/data-tools/bytes/lion/nyclion_26c.zip
unzip data/raw/lion/nyclion_26c.zip -d data/raw/lion
uv run python pipeline/course.py
uv run python pipeline/turns.py            # NYC on LION
uv run python pipeline/match.py            # every city: download OSM + snap the GPX guide (data/raw/gpx/<city>.gpx)
uv run python pipeline/turns.py nyc boston london berlin chicago tokyo sydney capetown
uv run python pipeline/export.py

# Web
cd web && npm install && npm run dev
```

## What this fork changes

**Result: CIM (2025 course), about +2,470 ft (0.47 mi) across 56 turns, or +2,720 ft (0.51 mi) corner to
corner.** That ranks it last of the nine races, just behind Boston: like Boston, it's a point-to-point course
(Folsom to the State Capitol) with long straight stretches on Folsom-Auburn Rd and Fair Oaks Blvd.

- **Course guide:** a Strava GPS track of the 2025 race (which hosted the USATF Marathon Championships), saved as
  `data/raw/gpx/cim.gpx` (not committed, like the other cities' GPX files). It's snapped onto OpenStreetMap by
  the unchanged `match.py`: 26.38 mi guide → 26.44 mi course, never more than 62 ft from the GPS track.
- **OSM data:** the public Overpass servers timed out on the course corridor, so CIM uses the repo's other OSM
  route: a local extract read with osmium, here [BBBike's Sacramento extract](https://download.bbbike.org/osm/bbbike/Sacramento/)
  (it reaches just past the Folsom start). Widths use the same lane-count rule as every other city.
- **One artifact rule added** (`turns.py`, `drop_artifacts`): OSM maps Fair Oaks Blvd at Sunrise Blvd as two
  one-way carriageways, and the snap hopped between them across Sunrise, making a fake +127° / −122° pair worth
  243 ft. Two opposite hairpins within 150 ft that cancel to within 30° are now dropped as a carriageway hop. No
  other city's published turns contain such a pair, so their numbers would not change.
- **`export.py`** now merges into the existing `cities.json` instead of rewriting it, so a city can be added
  without the other cities' raw data (LION, their GPX files).
- **Files touched:** `pipeline/cities.py` (CIM entry), `pipeline/osm.py` (Sacramento extract),
  `pipeline/turns.py`, `pipeline/export.py`, `web/public/data/cim/` (new), `web/public/data/cities.json`, and small
  copy changes in `web/index.html` / `web/src/main.js` ("Compare the Majors + CIM", a "CIM" label, a footer
  credit). Everything else, including the styling, is unchanged from the original.

To rebuild CIM:

```bash
curl -L -o data/raw/pbf/Sacramento.osm.pbf https://download.bbbike.org/osm/bbbike/Sacramento/Sacramento.osm.pbf
uv run python pipeline/match.py cim        # needs data/raw/gpx/cim.gpx
uv run python pipeline/turns.py cim
uv run python pipeline/export.py cim
```

## Credits

Built by [Dana Kraushar](https://www.linkedin.com/in/danakraushar/) with
[Claude Code](https://claude.com/claude-code) (Anthropic) as an AI pair programmer: Dana set the question,
made the design and method calls, and reviewed each step; Claude wrote most of the code and ran the analysis.

CIM addition: forked by [birdjc](https://github.com/birdjc), again with Claude Code, following Dana's method
unchanged apart from the notes above.

Data: [NYC LION](https://www.nyc.gov/content/planning/pages/resources/datasets/lion) (NYC Department of City
Planning). CIM streets: OpenStreetMap via [BBBike](https://extract.bbbike.org/) extracts. Basemap © CARTO, © OpenStreetMap contributors. Link-preview map: NYC Open Data
[Borough Boundaries](https://data.cityofnewyork.us/d/gthc-hcne) and US Census Bureau
[cartographic county boundaries](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html).
