import json
from pathlib import Path


# =====================================================
# NEWSLETTER DATA FILE
# =====================================================

DATA_FILE = Path("output/newsletter.json")


# =====================================================
# DEFAULT NEWSLETTER
# =====================================================

def get_default_newsletter_data():

    return {
        "date": None,
        "time_window": None,
        "news": [],
        "startups": [],
        "people": [],
        "tweets": [],
        "github_repos": [],
        "research_papers": [],
        "discovered_entities": [],
        "tool_of_the_day": None,
    }


# =====================================================
# LOAD NEWSLETTER
# =====================================================

def load_newsletter_data():

    # -------------------------------------------------
    # File does not exist
    # -------------------------------------------------

    if not DATA_FILE.exists():

        print(
            "Newsletter data file does not exist."
        )

        return get_default_newsletter_data()

    # -------------------------------------------------
    # Read existing newsletter
    # -------------------------------------------------

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # -------------------------------------------------
        # Make sure JSON is an object
        # -------------------------------------------------

        if not isinstance(
            data,
            dict
        ):

            print(
                "Newsletter data is not a valid JSON object."
            )

            return get_default_newsletter_data()

        # -------------------------------------------------
        # Add missing fields without destroying
        # existing newsletter content.
        # -------------------------------------------------

        defaults = get_default_newsletter_data()

        for key, default_value in defaults.items():

            if key not in data:

                data[key] = default_value

        return data

    # -------------------------------------------------
    # Invalid JSON / read failure
    # -------------------------------------------------

    except Exception as error:

        print(
            f"Failed to load newsletter data: {error}"
        )

        # IMPORTANT:
        # Do not create/overwrite the existing file here.
        # The caller receives safe fallback data instead.

        return get_default_newsletter_data()