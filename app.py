from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Step to get the authenticated user's GitHub username
def get_github_username():
    res = requests.get("https://api.github.com/user", headers=headers)
    return res.json().get("login")

@app.route('/create-repo', methods=['POST'])
def create_repo():
    data = request.json
    repo_name = data.get("team_name")
    username = data.get("github_username")

    # Step 1: Create repo under your account
    repo_res = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={"name": repo_name, "private": True}
    )

    if repo_res.status_code != 201:
        return jsonify({"error": repo_res.json()}), repo_res.status_code

    # Step 2: Get your GitHub username (as the repo owner)
    owner = get_github_username()

    # Step 3: Add collaborator
    collab_res = requests.put(
        f"https://api.github.com/repos/{owner}/{repo_name}/collaborators/{username}",
        headers=headers,
        json={"permission": "push"}
    )

    if collab_res.status_code not in [201, 204]:
        return jsonify({
            "warning": "Repo created but user could not be added",
            "details": collab_res.json()
        }), collab_res.status_code

    return jsonify({"message": "Repo created and user added!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
