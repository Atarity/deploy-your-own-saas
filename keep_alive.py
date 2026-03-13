import os
import json
import re
import urllib.request
import urllib.error
from datetime import datetime

def get_github_repo_info(github_url, token, etag=None):
    match = re.search(r'github\.com/([^/]+)/([^/#?]+)', github_url)
    if not match:
        return None

    owner = match.group(1)
    repo = match.group(2).replace('.git', '')

    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DYOS-DB-Enricher"
    }

    if etag:
        # Restore quotes if they were stripped for storage
        request_etag = etag if etag.startswith('"') else f'"{etag}"'
        headers["If-None-Match"] = request_etag

    req = urllib.request.Request(api_url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            if status == 200:
                data = json.loads(response.read().decode('utf-8'))
                raw_etag = response.headers.get("ETag")
                return {
                    "status": "ok",
                    "stars": data.get("stargazers_count", 0),
                    "pushed_at": data.get("pushed_at", ""),
                    "site": data.get("homepage") or "",
                    "etag": raw_etag.strip('"') if raw_etag else None
                }
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return {"status": "not_modified"}
        error_msg = f"HTTP Error {e.code}"
        print(f"Error fetching {github_url}: {error_msg}")
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = str(e)
        print(f"Exception for {github_url}: {error_msg}")
        return {"status": "error", "message": error_msg}
    return None

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GITHUB_ACCESS_TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None

def main():
    token = os.environ.get("GITHUB_ACCESS_TOKEN") or load_env()
    if not token:
        print("GITHUB_ACCESS_TOKEN not found in environment or .env file.")
        return

    db_path = "/Users/atarity/GitHub/deploy-your-own-saas/dyos-db.json"

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        print("Database file not found.")
        return

    updated_count = 0
    not_modified_count = 0
    archived_count = 0
    total_in_db = 0

    for group in db.get("groups", []):
        for project in group.get("projects", []):
            total_in_db += 1
            if project.get("archived"):
                archived_count += 1
                continue
            github_url = project.get("github")
            if github_url:
                current_etag = project.get("etag")
                info = get_github_repo_info(github_url, token, current_etag)

                if info:
                    if info["status"] == "ok":
                        project["stars"] = info["stars"]
                        project["pushed_at"] = info["pushed_at"]
                        if info["site"]:
                            project["site"] = info["site"]
                        project["etag"] = info["etag"]
                        project["error"] = None
                        updated_count += 1
                        print(f"Updated: {project['name']}")
                    elif info["status"] == "not_modified":
                        not_modified_count += 1
                        project["error"] = None
                        # print(f"Not modified: {project['name']}")
                    elif info["status"] == "error":
                        project["error"] = info["message"]

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    print(f"Done. Updated: {updated_count}, Not modified: {not_modified_count}, Archived: {archived_count}, Total in DB: {total_in_db}")

if __name__ == "__main__":
    main()
