"""Service for spatial query of districts, radar sites, and airports."""

import uuid
from typing import List, Optional
from apps.api.repositories.location_repository import LocationRepository
from apps.api.schemas.location import LocationSchema, LocationFilterParams


class LocationService:
    """Provides geographic references for operational nowcasting domains."""

    def __init__(self, location_repo: LocationRepository):
        self.location_repo = location_repo

    def list_locations(self, filters: Optional[LocationFilterParams] = None) -> List[LocationSchema]:
        """Returns geographic reference points."""
        db_locations = self.location_repo.get_all(filters)
        if db_locations:
            return [
                LocationSchema(
                    id=loc.id,
                    name=loc.name,
                    location_type=loc.location_type,
                    state=loc.state,
                    district=loc.district,
                    elevation_m=loc.elevation_m,
                    population=loc.population,
                    coordinates=[77.2090, 28.6139],
                )
                for loc in db_locations
            ]

        # Baseline reference sites in Delhi-NCR operational sector
        return [
            LocationSchema(
                id=uuid.UUID("44444444-4444-4444-4444-444444444441"),
                name="IMD Mausam Bhavan / Safdarjung DWR",
                location_type="RADAR_SITE",
                state="Delhi",
                district="New Delhi",
                elevation_m=216.0,
                coordinates=[77.2069, 28.5847],
            ),
            LocationSchema(
                id=uuid.UUID("44444444-4444-4444-4444-444444444442"),
                name="Indira Gandhi International Airport (Palam DWR)",
                location_type="AIRPORT",
                state="Delhi",
                district="South West Delhi",
                elevation_m=237.0,
                coordinates=[77.1000, 28.5562],
            ),
            LocationSchema(
                id=uuid.UUID("44444444-4444-4444-4444-444444444443"),
                name="Noida Sector 62 AWS",
                location_type="AWS_STATION",
                state="Uttar Pradesh",
                district="Gautam Buddha Nagar",
                elevation_m=200.0,
                coordinates=[77.3620, 28.6280],
            ),
            LocationSchema(
                id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
                name="Gurugram Cyber City AWS",
                location_type="AWS_STATION",
                state="Haryana",
                district="Gurugram",
                elevation_m=220.0,
                coordinates=[77.0878, 28.4950],
            ),
        ]
