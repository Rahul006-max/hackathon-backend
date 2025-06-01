from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

# GitHub token must be set in Render's environment variables
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Helper function to get your GitHub username (repo owner)
def get_github_username():
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code == 200:
        return res.json().get("login")
    return None

@app.route('/create-repo', methods=['POST'])
def create_repo():
    data = request.json
    repo_name = data.get("team_name")
    username = data.get("github_username")

    if not repo_name or not username:
        return jsonify({"error": "Missing 'team_name' or 'github_username'"}), 400

    # Step 1: Create the repository under the user's account
    repo_res = requests.post(
        "https://api.github.com/user/repos",
        headers=headers,
        json={"name": repo_name, "private": True}
    )

    if repo_res.status_code != 201:
        return jsonify({"error": repo_res.json()}), repo_res.status_code

    # Step 2: Get the GitHub username of the authenticated token owner
    owner = get_github_username()
    if not owner:
        return jsonify({"error": "Could not retrieve GitHub username"}), 500

    # Step 3: Add the specified user as a collaborator
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
