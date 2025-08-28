"""
Settings module for frete_proj.
Imports the appropriate settings module based on environment.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Determine which settings to use
ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT", "dev")

if ENVIRONMENT == "production":
    from .prod import *
else:
    from .dev import *
