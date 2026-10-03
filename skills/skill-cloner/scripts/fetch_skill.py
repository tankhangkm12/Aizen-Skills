import os
import sys
import shutil
import urllib.request
import json
import re

def fetch_github_folder(repo_api_url, dest_dir):
    req = urllib.request.Request(repo_api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for item in data:
                item_path = os.path.join(dest_dir, item['name'])
                if item['type'] == 'file':
                    print(f"Downloading {item['name']}...")
                    file_req = urllib.request.Request(item['download_url'], headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(file_req) as f_res:
                        with open(item_path, 'wb') as f_out:
                            f_out.write(f_res.read())
                elif item['type'] == 'dir':
                    os.makedirs(item_path, exist_ok=True)
                    fetch_github_folder(item['url'], item_path)
    except Exception as e:
        print(f"Error fetching {repo_api_url}: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_skill.py <source_url_or_path> <dest_skill_name>")
        sys.exit(1)
        
    source = sys.argv[1]
    dest_name = sys.argv[2]
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dest_dir = os.path.join(base_dir, dest_name)
    
    if os.path.exists(dest_dir):
        print(f"Warning: Destination {dest_dir} already exists. It will be overwritten.")
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Check if local path
    if os.path.exists(source):
        print(f"Copying local folder {source} to {dest_dir}")
        shutil.copytree(source, dest_dir, dirs_exist_ok=True)
        print("Done.")
        sys.exit(0)
        
    # Check if GitHub URL (e.g. https://github.com/anthropics/skills/tree/main/skills/pdf)
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)', source)
    if match:
        owner, repo, branch, path = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        print(f"Fetching from GitHub: {api_url}")
        fetch_github_folder(api_url, dest_dir)
        print("Done.")
        sys.exit(0)
        
    print("Error: Source must be a local directory or a GitHub tree URL (e.g., https://github.com/user/repo/tree/main/path)")
    sys.exit(1)

if __name__ == "__main__":
    main()
