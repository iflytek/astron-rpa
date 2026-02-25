import json
import os

import yaml

base_dir = os.path.dirname(__file__) + "/components"
# Define any directories to skip
# skipped_verse = ["astronverse-database"]

folders = os.listdir(base_dir)

# loop through each folder and read the config.yaml file


def merge_local_config():
    print("Merging local config.yaml files from component directories...")
    result = []
    for folder in folders:
        # if folder in skipped_verse:
        #     continue
        verse_folder = os.path.join(base_dir, folder)
        config_yaml_path = os.path.join(verse_folder, "config.yaml")
        if not os.path.isfile(config_yaml_path):
            continue
        with open(config_yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "atomic" in data:
                for atomic in data["atomic"]:
                    result.append({
                        "atomic": atomic,
                        "title": data["atomic"][atomic].get("title", ""),
                        "comment": data["atomic"][atomic].get("comment", "")
                    })
            else:
                print(f"\033[31mNo atomic key found in {config_yaml_path}\033[0m")

    # save to csv file
    with open(os.path.join(os.path.dirname(__file__), "temp_config.csv"), "w", encoding="utf-8") as f:
        f.write("atomic,title,comment\n")
        f.writelines(f"{item['atomic']},{item['title']},{item['comment']}\n" for item in result)
    return result


def input_list_check():
    print("Checking inputList in config.yaml files from component directories...")
    for folder in folders:
        verse_folder = os.path.join(base_dir, folder)
        config_yaml_path = os.path.join(verse_folder, "config.yaml")
        if not os.path.isfile(config_yaml_path):
            continue
        with open(config_yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "atomic" in data:
                for atomic in data["atomic"]:
                    if "inputList" not in data["atomic"][atomic]:
                        print(f"\033[31mNo inputList found in {config_yaml_path} for atomic {atomic}\033[0m")
            else:
                print(f"\033[31mNo atomic key found in {config_yaml_path}\033[0m")

if __name__ == "__main__":
    merge_local_config()