"""
API v1 Blueprint
Versioned API structure for Gut Health Management App
"""

from flask import Blueprint

bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import route modules to register their endpoints
from . import diary
from . import recipes
from . import foods
from . import analytics
from . import usda
from . import ausnut
from . import settings
from . import education
from . import chat
from . import fodmap
from . import search
from . import export
from . import realtime
# New modules for App2 integration (v1.2.0)
from . import reintroduction
from . import notifications
from . import gamification
from . import integrations
from . import billing
from . import security
from . import multi_user
