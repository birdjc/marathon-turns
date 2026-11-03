"""The eight Abbott World Marathon Majors plus seven more big races (CIM, Marine Corps, Houston, Los Angeles,
Philadelphia, Valencia, Grandma's), and where each course comes from.

Course guides are third-party GPX tracks from goandrace.com (most recent edition available); CIM's is a Strava
GPS track of the 2025 race (which hosted the USATF Marathon Championships). They're only used as a guide: the course itself is snapped onto OpenStreetMap streets (see match.py).
"""

from dataclasses import dataclass, field

from lion import ROOT

GPX_DIR = ROOT / "data/raw/gpx"


@dataclass
class City:
    slug: str
    name: str            # "Berlin Marathon"
    city: str            # "Berlin"
    edition: int         # year of the course we measure
    gpx_source: str      # course map page the GPX came from (goandrace, or the race's own page)
    # Optional (mile, label) chart sections, like NYC's boroughs.
    sections: list = field(default_factory=list)

    @property
    def gpx(self):
        return GPX_DIR / f"{self.slug}.gpx"


GOANDRACE = "https://goandrace.com/en/map/"
CITIES = {c.slug: c for c in [
    City("nyc", "New York City Marathon", "New York", 2026,
         GOANDRACE + "2025/tcs-new-york-city-marathon-2025-course-map-1.php",
         sections=[(0, "SI"), (1.9, "Brooklyn"), (13.1, "Qns"), (15.5, "Man"), (19.5, "Bx"), (20.8, "Man")]),
    City("boston", "Boston Marathon", "Boston", 2026, GOANDRACE + "2026/boston-marathon-2026-boston-course-map-1.php"),
    City("london", "London Marathon", "London", 2025, GOANDRACE + "2025/tcs-london-marathon-2025-course-map-1.php"),
    City("berlin", "Berlin Marathon", "Berlin", 2025, GOANDRACE + "2025/bmw-berlin-marathon-2025-course-map-1.php"),
    City("chicago", "Chicago Marathon", "Chicago", 2025,
         GOANDRACE + "2025/bank-of-america-chicago-marathon-2025-course-map-1.php"),
    City("tokyo", "Tokyo Marathon", "Tokyo", 2025, GOANDRACE + "2025/tokyo-marathon-2025-tokyo-course-map-1.php"),
    City("sydney", "Sydney Marathon", "Sydney", 2025, GOANDRACE + "2025/tcs-sydney-marathon-2025-course-map-1.php"),
    City("capetown", "Cape Town Marathon", "Cape Town", 2024,
         GOANDRACE + "2024/sanlam-cape-town-marathon-2024-course-map-1.php"),
    City("cim", "California International Marathon", "Sacramento", 2025,
         "https://www.runsra.org/california-international-marathon"),
    City("mcm", "Marine Corps Marathon", "Washington", 2024,
         GOANDRACE + "2024/marine-marathon-2024-arlington-course-map-2.php"),
    City("houston", "Chevron Houston Marathon", "Houston", 2026,
         GOANDRACE + "2026/chevron-houston-marathon-2026-course-map-1.php"),
    City("la", "Los Angeles Marathon", "Los Angeles", 2026,
         GOANDRACE + "2026/los-angeles-marathon-2026-los-angeles-course-map-1.php"),
    City("philly", "Philadelphia Marathon", "Philadelphia", 2025,
         GOANDRACE + "2025/philadelphia-marathon-2025-philadelphia-course-map-1.php"),
    City("valencia", "Valencia Marathon", "Valencia", 2025,
         GOANDRACE + "2025/valencia-marathon-2025-valencia-course-map-1.php"),
    City("grandmas", "Grandma's Marathon", "Duluth", 2025,
         GOANDRACE + "2025/grandma-s-marathon-2025-duluth-course-map-1.php"),
]}
