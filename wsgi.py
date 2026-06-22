"""WSGI entry point for Render/Gunicorn deployment."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from motorcycle_registration.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
