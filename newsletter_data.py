import json
import os

import psycopg
from dotenv import load_dotenv


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# DATABASE
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    return psycopg.connect(
        DATABASE_URL
    )


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
# SAVE NEWSLETTER
# =====================================================

def save_newsletter_data(
    data: dict
):

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "Newsletter data must be a JSON object."
        )

    try:

        with get_connection() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO newsletters (data)
                    VALUES (%s)
                    """,
                    (
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ),
                    ),
                )

            conn.commit()

    except Exception as error:

        print(
            f"Failed to save newsletter data: {error}"
        )

        raise


# =====================================================
# LOAD LATEST NEWSLETTER
# =====================================================

def load_newsletter_data():

    try:

        with get_connection() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT data
                    FROM newsletters
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1
                    """
                )

                row = cur.fetchone()

                # -------------------------------------------------
                # No newsletter stored yet
                # -------------------------------------------------

                if not row:

                    print(
                        "No newsletter found in database."
                    )

                    return get_default_newsletter_data()

                data = row[0]

                # -------------------------------------------------
                # Convert JSON string if necessary
                # -------------------------------------------------

                if isinstance(
                    data,
                    str
                ):

                    data = json.loads(
                        data
                    )

                # -------------------------------------------------
                # Make sure data is an object
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

    except Exception as error:

        print(
            f"Failed to load newsletter data: {error}"
        )

        # IMPORTANT:
        # Do not overwrite database data on failure.
        # Return safe fallback data instead.

        return get_default_newsletter_data()