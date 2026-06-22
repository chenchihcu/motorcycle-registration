#!/usr/bin/env python3
"""
Netlify deploy script - uploads Flask app as serverless function via REST API.
Bypasses the broken CLI zip-it-and-ship-it Python detection.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

NETLIFY_SITE_ID = "6bf231d6-1293-410b-aa5d-c77f942f71be"
API_BASE = "https://api.netlify.com/api/v1"


def get_token():
    """Get Netlify auth token from CLI config."""
    # Try multiple locations
    paths = [
        os.path.expanduser("~/.netlify/config.json"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "netlify", "Config.json"),
        os.path.join(os.environ.get("APPDATA", ""), "netlify", "Config.json"),
    ]
    for p in paths:
        if os.path.isfile(p):
            with open(p) as f:
                cfg = json.load(f)
            token = cfg.get("accessToken") or cfg.get("_authToken")
            if token:
                return token
    # Try environment
    token = os.environ.get("NETLIFY_AUTH_TOKEN")
    if token:
        return token
    raise RuntimeError("No Netlify auth token found")


def build_function_zip(source_dir, output_path):
    """Create a deployment-ready zip of the Flask app as a Netlify function."""
    # Create a temp dir for the function bundle
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy the Flask app files (excluding __pycache__, .omo, .netlify)
        app_dir = os.path.join(tmpdir, "app")
        shutil.copytree(source_dir, app_dir, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".omo", ".netlify", "instance", ".env"
        ))

        # Create a wrapper handler
        handler_content = """import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from serverless_wsgi import handle
from app import create_app

app = create_app()

def handler(event, context):
    return handle(app, event, context)
"""
        # Use the existing api.py
        api_py = os.path.join(app_dir, "netlify", "functions", "api.py")
        if os.path.isfile(api_py):
            with open(api_py) as f:
                handler_content = f.read()

        wsgi_handler = os.path.join(app_dir, "handler.py")
        with open(wsgi_handler, "w") as f:
            f.write("# Wrapper for Netlify detection\n")

        # Create zip at output_path
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(app_dir):
                for fn in files:
                    filepath = os.path.join(root, fn)
                    arcname = os.path.relpath(filepath, app_dir)
                    zf.write(filepath, arcname)

    return output_path


def deploy(headers):
    """Create a new deploy and upload files."""
    pub_dir = os.path.join(os.path.dirname(__file__), "motorcycle_registration")

    # Step 1: Create deploy
    print("Creating deploy...")
    resp = requests.post(
        f"{API_BASE}/sites/{NETLIFY_SITE_ID}/deploys",
        headers=headers,
        json={"async": False},
    )
    resp.raise_for_status()
    deploy_data = resp.json()
    deploy_id = deploy_data["id"]
    required = deploy_data.get("required", [])
    print(f"Deploy ID: {deploy_id}")
    print(f"Required files: {len(required)}")

    # Step 2: Upload static files
    file_shas = {}
    for root, dirs, files in os.walk(pub_dir):
        # Skip ignored dirs
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".omo", ".netlify", "instance")]
        for fn in files:
            filepath = os.path.join(root, fn)
            arcname = os.path.relpath(filepath, pub_dir).replace("\\", "/")
            with open(filepath, "rb") as f:
                data = f.read()
            resp = requests.put(
                f"{API_BASE}/deploys/{deploy_id}/files/{arcname}",
                headers={**headers, "Content-Type": "application/octet-stream"},
                data=data,
            )
            if resp.status_code == 200:
                print(f"  Uploaded: {arcname} ({len(data)} bytes)")
                file_shas[arcname] = resp.json().get("sha")
            else:
                print(f"  Failed: {arcname} ({resp.status_code})")

    # Step 3: Build and upload function zip
    print("\nBuilding function zip...")
    func_zip = os.path.join(tempfile.gettempdir(), "netlify-function.zip")
    build_function_zip(pub_dir, func_zip)
    zip_size = os.path.getsize(func_zip)

    print(f"Uploading function zip ({zip_size} bytes)...")
    with open(func_zip, "rb") as f:
        resp = requests.put(
            f"{API_BASE}/deploys/{deploy_id}/functions/api",
            headers={**headers, "Content-Type": "application/zip"},
            data=f,
        )
    if resp.status_code == 200:
        print(f"  Function 'api' uploaded successfully")
    else:
        print(f"  Function upload failed: {resp.status_code} {resp.text}")

    # Clean up
    os.unlink(func_zip)

    return deploy_data


def main():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    result = deploy(headers)
    print(f"\n✅ Deploy complete!")
    print(f"URL: {result.get('ssl_url', result.get('url', '?'))}")
    print(f"Admin: https://app.netlify.com/projects/{NETLIFY_SITE_ID}")


if __name__ == "__main__":
    main()
