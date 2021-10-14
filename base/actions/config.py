import os

GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", None)
EVENTSTORE_URL = os.environ.get("EVENTSTORE_URL", None)
EVENTSTORE_TOKEN = os.environ.get("EVENTSTORE_TOKEN", None)
HTTP_RETRIES = int(os.environ.get("HTTP_RETRIES", 3))
SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
STUDY_A_MESSAGE_DELAY = float(os.environ.get("STUDY_A_MESSAGE_DELAY", 0.5))
