from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = os.environ.get("GITHUB_ORG")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

@app.route('/create-repo', methods=['POST'])
def create_repo():
    data = request.json
    repo_name = data.get("team_name")
    username = data.get("github_username")

    # Step 1: Create repo
    repo_res = requests.post(
        f"https://api.github.com/orgs/{GITHUB_ORG}/repos",
        headers=headers,
        json={"name": repo_name, "private": True}
    )

    if repo_res.status_code != 201:
        return jsonify({"error": repo_res.json()}), repo_res.status_code

    # Step 2: Add user as collaborator
    collab_res = requests.put(
        f"https://api.github.com/repos/{GITHUB_ORG}/{repo_name}/collaborators/{username}",
        headers=headers,
        json={"permission": "push"}
    )

    return jsonify({"message": "Repo created and user added!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
