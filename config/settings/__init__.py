from decouple import config

ENVIRONMENT = config("DJANGO_ENV")

if ENVIRONMENT == "development":
    from .development import *
elif ENVIRONMENT == "testing":
    from .testing import *
elif ENVIRONMENT == "production":
    from .production import *
else:
    msg = "Invalid DJANGO_ENV value"
    raise ValueError(msg)
