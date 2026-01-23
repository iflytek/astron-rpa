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
remote_tree_url = os.getenv("REMOTE_TREE_URL", "your remote tree url address in .env file")
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
            print(f"\033[31mFailed to run meta.py in {verse_folder}: {e}\033[0m")


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
        result = response.json()
        if response.status_code == 200 and isinstance(result, list):
            save_json_to_file(result, os.path.join(os.path.dirname(__file__), "temp_remote.json"))
            return result
        else:
            print(f"\033[31mFailed to get remote meta. Status code: {response.status_code}. response: {result} \033[0m")
            return None
    except Exception as e:
        print(f"\033[31mError getting remote meta.json: {e}\033[0m")
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
    print(f"Found {len(new_items)} new items")
    if new_items:
        remote_meta.extend(new_items)

    remote_meta = sort_meta_items(remote_meta)
    save_json_to_file(remote_meta, os.path.join(os.path.dirname(__file__), "temp_update.json"))
    return remote_meta


def sort_meta_items(meta_items):
    return sorted(meta_items, key=lambda x: (x.get("atomKey") is None, x.get("atomKey")))


def meta_upload():
    update_json_path = os.path.join(os.path.dirname(__file__), "temp_update.json")
    with open(update_json_path, encoding="utf-8") as f:
        update_meta = json.load(f)
        print(f"Uploading {len(update_meta)} meta items to server...")
        try:
            response = requests.post(upload_url, json=update_meta, timeout=10)
            if response.status_code == 200:
                print("\033[32mmeta uploaded successfully.\033[0m")
            else:
                print(f"\033[31mFailed to upload meta. Status code: {response.status_code}\033[0m")
        except Exception as e:
            print(f"\033[31mError uploading meta: {e}\033[0m")


def get_remote_tree():
    print("Fetching remote tree from server...")
    response = requests.post(remote_tree_url, timeout=10)
    if response.status_code == 200:
        res = response.json().get("data", {})
        # res may be a JSON string; parse it to a Python object
        if isinstance(res, str):
            try:
                res_json = json.loads(res)
                save_json_to_file(res_json, os.path.join(os.path.dirname(__file__), "temp_tree.json"))
            except json.JSONDecodeError as e:
                print(f"\033[31mError parsing remote tree JSON: {e}\033[0m")
                return

    else:
        print(f"\033[31mFailed to get remote tree. Status code: {response.status_code}\033[0m")


def tree_upload():
    with open(os.path.join(os.path.dirname(__file__), "temp_tree.json"), encoding="utf-8") as f:
        tree_data = json.load(f)
    try:
        response = requests.post(tree_upload_url, json=tree_data, timeout=10)
        if response.status_code == 200:
            print("\033[32mtree uploaded successfully.\033[0m")
        else:
            print(f"\033[31mFailed to upload tree. Status code: {response.status_code}\033[0m")
    except Exception as e:
        print(f"\033[31mError uploading tree: {e}\033[0m")


def save_json_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    local_meta = None
    remote_meta = None
    # Prompt user for actions
    choice = input("Do you want to run meta? (Y/N): ").strip().lower()
    if choice == "y":
        run_meta_scripts()
        local_meta = merge_local_meta()
    else:
        print("\033[33mSkipping run meta and merge. load from temp_local.json if exists.\033[0m")
        with open(os.path.join(os.path.dirname(__file__), "temp_local.json"), encoding="utf-8") as f:
            local_meta = json.load(f)

    remote_meta = get_remote_meta()

    if local_meta and remote_meta:
        choice = input("Do you want to merge local meta with remote meta? (Y/N): ").strip().lower()
        if choice == "y":
            merge_local_and_remote(local_meta, remote_meta)
        else:
            print("\033[33mSkipping merge. load from temp_update.json if exists.\033[0m")
        choice = input("Do you want to upload the updated meta to the server? (Y/N): ").strip().lower()
        if choice == "y":
            print("Uploading updated meta to the server...")
            meta_upload()
        else:
            print("\033[33mUpload skipped.\033[0m")

    get_remote_tree()
    choice = input("Do you want to update tree to the server? (Y/N): ").strip().lower()
    if choice == "y":
        print("Uploading tree to the server...")
        tree_upload()
    else:
        print("\033[33mTree upload skipped.\033[0m")
