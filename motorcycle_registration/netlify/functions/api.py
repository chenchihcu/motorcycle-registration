import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from serverless_wsgi import handle
from app import create_app

app = create_app()


def handler(event, context):
    """Netlify Function handler - wraps Flask app using serverless-wsgi"""
    return handle(app, event, context)
