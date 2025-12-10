import json
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
upload_url = os.getenv("COMPONENTS_META_UPLOAD_URL", "your meta upload url address in .env file")
# Define the base directory for components
base_dir = os.path.dirname(__file__) + "/components"
# Define any directories to skip
skiped_verse = ["astronverse-database"]


# run meta.py in each component directory
def run_meta_scripts():
    for folder in os.listdir(base_dir):
        if folder in skiped_verse:
            continue
        verse_folder = os.path.join(base_dir, folder)
        meta_script = os.path.join(verse_folder, "meta.py")
        if not os.path.isfile(meta_script):
            continue
        print(f"Running meta.py in {verse_folder}")

        # Run meta.py using the proper Python interpreter
        try:
            subprocess.run([sys.executable, "meta.py"], cwd=verse_folder, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run meta.py in {verse_folder}: {e}")


# Aggregate meta.json files from each component directory
def run_meta_json():
    result = {}
    for folder in os.listdir(base_dir):
        if folder in skiped_verse:
            continue
        verse_folder = os.path.join(base_dir, folder)
        meta_json_path = os.path.join(verse_folder, "meta.json")
        if not os.path.isfile(meta_json_path):
            continue
        print(f"Loading meta.json from {verse_folder}")
        with open(meta_json_path, encoding="utf-8") as f:
            data = json.load(f)
            result.update(data)

    return result


# Generate a temporary JSON file with aggregated data
def gen_temp_json(data: dict):
    if not data:
        print("No data to write to temp.json")
        return
    counts_verse = len(data)
    print(f"Generating temp.json with {counts_verse} verses")
    temp_path = os.path.join(os.path.dirname(__file__), "meta.json")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_meta_scripts()
    meta_data = run_meta_json()
    if meta_data:
        gen_temp_json(meta_data)
        print("meta.json generated successfully.")
        # upload to server
        response = requests.post(upload_url, json=meta_data, timeout=10)
        if response.status_code == 200:
            print("meta.json uploaded successfully.")
