"""WSGI entry point for Render/Gunicorn deployment."""
import sys
import os

_repo_root = os.path.dirname(__file__)
sys.path.insert(0, _repo_root)
sys.path.insert(0, os.path.join(_repo_root, 'motorcycle_registration'))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
