English | [简体中文](README.zh.md)
# Automatic Build and Update of Meta Configuration Guide 

This project uses the `meta_json.py` script to automatically build, merge, and upload component meta configurations. The following are the instructions for use:

## Features

- Automatically execute `meta.py` in each component directory to generate/update the local `meta.json`.
- Merge all component `meta.json` files into a single master configuration.
- Pull the meta configuration from the remote server and merge it with the local configuration to avoid losing existing content on the server.
- Support uploading the merged configuration to the server.

## Environment Setup

1. Install dependencies:
  ```bash
  pip install requests python-dotenv
  ```
2. Create a `.env` file in the project root directory and configure the following environment variables:
  ```
  COMPONENTS_META_UPLOAD_URL=your_meta_upload_api_url
  REMOTE_META_URL=your_remote_meta_fetch_api_url
  ```

## How to Use

1. Navigate to the `engine` directory:
  ```bash
  cd engine
  ```
2. Run the script:
  ```bash
  python meta_json.py
  ```
3. Follow the prompts to confirm whether to upload the merged meta configuration to the server.

## Workflow

1. **Execute component meta.py**  
  The script automatically traverses the `components` directory, skips `astronverse-database`, and executes `meta.py` in each component's subdirectory to generate/update the corresponding `meta.json`.

2. **Merge local meta.json files**  
  It aggregates all component `meta.json` files and creates a temporary file `temp_local.json`.

3. **Fetch remote meta configuration**  
  It retrieves the meta configuration from the server via an API call and saves it as `temp_remote.json`.

4. **Merge local and remote meta**  
  It merges new or updated configurations from the local files into the remote meta list, generating `temp_update.json`.

5. **Upload the updated meta**  
  Based on user input, it decides whether to upload the merged meta configuration to the server.

## Notes

- Please ensure that the API URLs in the `.env` file are correct and accessible. You can refer to `.env.example`.
- The merge logic prioritizes local changes; any content not present in the remote configuration will be added.
- The upload operation is irreversible. Please confirm with caution.

If you have any questions, please contact the project maintainer.
