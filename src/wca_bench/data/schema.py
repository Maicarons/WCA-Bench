"""WCA export schema constants (v2.x snake_case)."""

from __future__ import annotations

from typing import Final

# Special result values
DNF: Final[int] = -1
DNS: Final[int] = -2
NO_RESULT: Final[int] = 0

# Round formats (WCA formats table)
FORMATS: Final[dict[str, dict]] = {
    "1": {"id": "1", "name": "Best of 1", "short": "bo1", "attempts": 1, "average": False},
    "2": {"id": "2", "name": "Best of 2", "short": "bo2", "attempts": 2, "average": False},
    "3": {"id": "3", "name": "Best of 3", "short": "bo3", "attempts": 3, "average": False},
    "a": {"id": "a", "name": "Average of 5", "short": "ao5", "attempts": 5, "average": True},
    "m": {"id": "m", "name": "Mean of 3", "short": "mo3", "attempts": 3, "average": True},
}

# Round types
ROUND_TYPES: Final[dict[str, str]] = {
    "0": "Qualification",
    "b": "B Final",
    "c": "Combined First",
    "d": "Combined Second",
    "e": "Combined Third",
    "f": "Final",
    "g": "Semi Final",
    "h": "Combined Final",
    "1": "First Round",
    "2": "Second Round",
    "3": "Third Round",
}

# Active WCA events + measurement format
# format: time | number | multi
EVENT_FORMATS: Final[dict[str, dict]] = {
    "333": {"name": "3x3x3 Cube", "format": "time", "group": "speed"},
    "222": {"name": "2x2x2 Cube", "format": "time", "group": "speed"},
    "444": {"name": "4x4x4 Cube", "format": "time", "group": "speed"},
    "555": {"name": "5x5x5 Cube", "format": "time", "group": "speed"},
    "666": {"name": "6x6x6 Cube", "format": "time", "group": "speed"},
    "777": {"name": "7x7x7 Cube", "format": "time", "group": "speed"},
    "333bf": {"name": "3x3x3 Blindfolded", "format": "time", "group": "blind"},
    "333oh": {"name": "3x3x3 One-Handed", "format": "time", "group": "other"},
    "333fm": {"name": "3x3x3 Fewest Moves", "format": "number", "group": "other"},
    "333ft": {"name": "3x3x3 With Feet", "format": "time", "group": "other"},
    "minx": {"name": "Megaminx", "format": "time", "group": "other"},
    "pyram": {"name": "Pyraminx", "format": "time", "group": "other"},
    "clock": {"name": "Clock", "format": "time", "group": "other"},
    "skewb": {"name": "Skewb", "format": "time", "group": "other"},
    "sq1": {"name": "Square-1", "format": "time", "group": "other"},
    "444bf": {"name": "4x4x4 Blindfolded", "format": "time", "group": "blind"},
    "555bf": {"name": "5x5x5 Blindfolded", "format": "time", "group": "blind"},
    "333mbf": {"name": "3x3x3 Multi-Blind", "format": "multi", "group": "blind"},
}

CONTINENT_ISO2_TO_NAME: Final[dict[str, str]] = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",
    "OC": "Oceania",
    "SA": "South America",
}

CONTINENT_NAME_TO_ID: Final[dict[str, str]] = {v: k for k, v in CONTINENT_ISO2_TO_NAME.items()}

# Default TSV file names (WCA export v2)
RAW_TABLE_FILES: Final[dict[str, str]] = {
    "persons": "WCA_export_Persons.tsv",
    "competitions": "WCA_export_Competitions.tsv",
    "results": "WCA_export_Results.tsv",
    "result_attempts": "WCA_export_ResultAttempts.tsv",
    "scrambles": "WCA_export_Scrambles.tsv",
    "events": "WCA_export_Events.tsv",
    "formats": "WCA_export_Formats.tsv",
    "round_types": "WCA_export_RoundTypes.tsv",
    "countries": "WCA_export_Countries.tsv",
    "continents": "WCA_export_Continents.tsv",
    "championships": "WCA_export_Championships.tsv",
    "eligible_country_iso2s_for_championship": (
        "WCA_export_EligibleCountryIso2sForChampionship.tsv"
    ),
}

RESULT_COLUMNS: Final[list[str]] = [
    "id",
    "pos",
    "person_id",
    "person_name",
    "country_id",
    "competition_id",
    "event_id",
    "round_type_id",
    "format_id",
    "best",
    "average",
    "regional_single_record",
    "regional_average_record",
]

ATTEMPT_COLUMNS: Final[list[str]] = [
    "result_id",
    "attempt_number",
    "value",
]

PERSON_COLUMNS: Final[list[str]] = [
    "wca_id",
    "sub_id",
    "name",
    "country_id",
    "gender",
    "birth_year",
    "birth_month",
]

COMPETITION_COLUMNS: Final[list[str]] = [
    "id",
    "name",
    "city_name",
    "country_id",
    "start_date",
    "end_date",
    "latitude_microdegrees",
    "longitude_microdegrees",
]
