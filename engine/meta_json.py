import json
import os
import subprocess
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
upload_url = os.getenv("COMPONENTS_META_UPLOAD_URL", "your meta upload url address in .env file")
remote_meta_url = os.getenv("REMOTE_META_URL", "your remote meta url address in .env file")
tree_upload_url = os.getenv("TREE_UPLOAD_URL", "your tree upload url address in .env file")
# Define the base directory for components
base_dir = os.path.dirname(__file__) + "/components"
# Define any directories to skip
skiped_verse = ["astronverse-database"]


# run meta.py in each component directory
def run_meta_scripts():
    print("Running meta.py scripts in component directories...")
    for folder in os.listdir(base_dir):
        if folder in skiped_verse:
            continue
        verse_folder = os.path.join(base_dir, folder)
        meta_script = os.path.join(verse_folder, "meta.py")
        if not os.path.isfile(meta_script):
            continue
        print(f"Running meta.py in {verse_folder}...")
        # Run meta.py using the proper Python interpreter
        try:
            subprocess.run([sys.executable, "meta.py"], cwd=verse_folder, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run meta.py in {verse_folder}: {e}")


# Aggregate meta.json files from each component directory
def merge_local_meta():
    print("Merging local meta.json files from component directories...")
    result = {}
    for folder in os.listdir(base_dir):
        if folder in skiped_verse:
            continue
        verse_folder = os.path.join(base_dir, folder)
        meta_json_path = os.path.join(verse_folder, "meta.json")
        if not os.path.isfile(meta_json_path):
            continue
        with open(meta_json_path, encoding="utf-8") as f:
            data = json.load(f)
            result.update(data)
    save_json_to_file(result, os.path.join(os.path.dirname(__file__), "temp_local.json"))
    return result


# Generate a temporary JSON file with aggregated data
def gen_temp_json(data: dict):
    if not data:
        print("No data to write to temp_local.json")
        return
    print(f"Generating meta.json with {len(data)} verses")
    save_json_to_file(data, os.path.join(os.path.dirname(__file__), "temp_local.json"))


def get_remote_meta():
    print("Fetching remote meta list from server...")
    try:
        response = requests.post(remote_meta_url, timeout=10)
        if response.status_code == 200:
            save_json_to_file(response.json(), os.path.join(os.path.dirname(__file__), "temp_remote.json"))
            return response.json()
        else:
            print(f"Failed to get remote meta. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting remote meta.json: {e}")
        return None


def merge_local_and_remote(local_meta: dict, remote_meta: list):
    print("Merging local meta with remote meta ...")
    new_items = []
    for key, value in local_meta.items():
        found = False
        for remote_item in remote_meta:
            if remote_item.get("atomKey") == key:
                remote_item["atomContent"] = json.dumps(value, ensure_ascii=False)
                found = True
                break
        if not found:
            new_item = {"atomKey": key, "atomContent": json.dumps(value, ensure_ascii=False), "sort": None}
            new_items.append(new_item)
    print(f"Found {len(new_items)} new items to add to remote meta.json.")
    if new_items:
        remote_meta.extend(new_items)

    remote_meta = sort_meta_items(remote_meta)
    save_json_to_file(remote_meta, os.path.join(os.path.dirname(__file__), "temp_update.json"))
    return remote_meta


def sort_meta_items(meta_items):
    return sorted(meta_items, key=lambda x: (x.get("atomKey") is None, x.get("atomKey")))


def meta_upload(meta_data):
    try:
        response = requests.post(upload_url, json=meta_data, timeout=10)
        if response.status_code == 200:
            print("meta uploaded successfully.")
        else:
            print(f"Failed to upload meta. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error uploading meta: {e}")


def tree_upload():
    with open(os.path.join(os.path.dirname(__file__), "temp_tree.json"), encoding="utf-8") as f:
        tree_data = json.load(f)
    try:
        response = requests.post(tree_upload_url, json=tree_data, timeout=10)
        if response.status_code == 200:
            print("tree uploaded successfully.")
        else:
            print(f"Failed to upload tree. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error uploading tree: {e}")


def save_json_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_meta_scripts()
    local_meta = merge_local_meta()
    if local_meta:
        remote_meta = get_remote_meta()
        if remote_meta:
            updated_meta = merge_local_and_remote(local_meta, remote_meta)
            choice = input("Do you want to upload the updated meta to the server? (Y/N): ").strip().lower()
            if choice == "y":
                print("Uploading updated meta to the server...")
                meta_upload(updated_meta)
            else:
                print("Upload skipped.")
