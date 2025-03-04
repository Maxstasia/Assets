# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_graph.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/03/04 15:52:20 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import requests
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

# 📌 Ton identifiant GitHub (Change-le par ton vrai username)
GITHUB_USERNAME = "Maxstasia"

# 📌 Ton token GitHub (utilisé uniquement en local, sinon stocke-le comme secret dans GitHub Actions)
GITHUB_TOKEN = os.getenv("GH_PAT")

if not GITHUB_TOKEN:
    raise ValueError("❌ ERREUR : Le token GitHub est manquant. Vérifie que le secret 'GH_PAT' est bien défini.")

print(f"🔑 Token récupéré : {GITHUB_TOKEN[:5]}...")  # Affiche les 5 premiers caractères pour vérifier

# 📌 Headers pour l'authentification API GitHub
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# 📌 Récupère tous les repos publics et privés de l'utilisateur
def get_repositories():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    #url = "https://api.github.com/user/repos?per_page=100"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ ERREUR API : {response.status_code} - {response.text}")  # Affiche l'erreur complète

    response.raise_for_status()
    return response.json()
    #return [repo["full_name"] for repo in response.json()]

repos = get_repositories()
print(f"✅ {len(repos)} repos récupérés !")

for repo in repos:
    print(f"📂 {repo['name']} - {repo['html_url']}")

# 📌 Récupère les commits des 12 derniers mois pour un repo donné
def get_commit_history(repo):
    since_date = (datetime.now() - timedelta(days=365)).isoformat()
    url = f"https://api.github.com/repos/{repo['full_name']}/commits?since={since_date}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    commits = []
    for commit in response.json():
        commit_hash = commit["sha"]
        commit_date = commit["commit"]["committer"]["date"]
        commit_url = commit["html_url"]
        commits.append((repo["full_name"], commit_hash, commit_date, commit_url))

    return commits

# 📌 Récupération des commits pour tous les repos
#repos = get_repositories()
all_commits = []
for repo in repos:
    all_commits.extend(get_commit_history(repo))

# 📌 Transformation en DataFrame
df = pd.DataFrame(all_commits, columns=["repo", "hash", "date", "url"])
df["repo"] = df["repo"].astype(str)  # 🔥 Ajout de cette ligne !
df["date"] = pd.to_datetime(df["date"])
df["week"] = df["date"].dt.isocalendar().week
df["year"] = df["date"].dt.isocalendar().year
df["day_of_week"] = df["date"].dt.weekday
df["formatted_date"] = df["date"].dt.strftime("%A %d %B %Y")

# 📌 Comptage des commits
df_count = df.groupby(["year", "week", "day_of_week", "repo"]).size().reset_index(name="count")
df_count = df_count.merge(df[["repo", "year", "week", "day_of_week", "formatted_date"]], 
                          on=["repo", "year", "week", "day_of_week"], 
                          how="left")
hover_text = df_count["repo"] + " - " + df_count["year"].astype(str) + "-S" + df_count["week"].astype(str) + "<br>" + df_count["formatted_date"]

# 📌 Création du graphique avec liens cliquables
fig = px.scatter_3d(
    df_count,
    x="week",
    y="day_of_week",
    z="count",
    color="repo",
    size="count",
    hover_name=hover_text,  # ✅ Ajout de la date formatée
    labels={"week": "Semaine", "day_of_week": "Jour", "count": "Commits"},
    title="Historique des Commits GitHub (1 an)"
)

# 📌 Enregistrement du fichier
output_dir1 = "../../Images/Graph/"
os.makedirs(output_dir1, exist_ok=True)  # Crée le dossier si inexistant
fig.write_image(os.path.join(output_dir1, "commit_graph.png"))
output_dir2 = "../../"
os.makedirs(output_dir2, exist_ok=True)  # Crée le dossier si inexistant
fig.write_html(os.path.join(output_dir2, "index.html"))

print("✅ Graphique généré : commit_graph.png et index.html")
