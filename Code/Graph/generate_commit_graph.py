# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_graph.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/03/04 17:47:52 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import requests
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

# 📌 Ton identifiant GitHub
GITHUB_USERNAME = "Maxstasia"

# 📌 Ton token GitHub
GITHUB_TOKEN = os.getenv("GH_PAT")
if not GITHUB_TOKEN:
    raise ValueError("❌ ERREUR : Le token GitHub est manquant.")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# 📌 Récupérer tous les repos publics et privés
def get_repositories():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

repos = get_repositories()
print(f"✅ {len(repos)} repos récupérés !")

for repo in repos:
    print(f"📂 {repo['name']} - {repo['html_url']}")

# 📌 Récupérer les commits des 12 derniers mois
def get_commit_history(repo):
    since_date = (datetime.now() - timedelta(days=365)).isoformat()
    url = f"https://api.github.com/repos/{repo['full_name']}/commits?since={since_date}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    commits = []
    for commit in response.json():
        commits.append((repo["full_name"], commit["sha"], commit["commit"]["committer"]["date"], commit["html_url"]))

    return commits

# 📌 Collecter tous les commits
all_commits = []
for repo in repos:
    all_commits.extend(get_commit_history(repo))

# 📌 Transformation en DataFrame
df = pd.DataFrame(all_commits, columns=["repo", "hash", "date", "url"])
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

# 📌 🔥 Amélioration du graphisme 🔥
fig = px.scatter_3d(
    df_count,
    x="week",
    y="day_of_week",
    z="count",
    color="repo",
    size=df_count["count"] * 4,  # Augmente la taille des points
    hover_name=hover_text,
    labels={"week": "Semaine", "day_of_week": "Jour", "count": "Commits"},
    title="📈 Historique des Commits GitHub (1 an)",
    template="plotly_dark"  # Applique un fond noir et un style sombre
)

# 📌 Personnalisation des axes et de l'apparence générale
fig.update_layout(
    scene=dict(
        xaxis=dict(title="Semaine", gridcolor="gray", zerolinecolor="white"),
        yaxis=dict(title="Jour de la semaine", gridcolor="gray", zerolinecolor="white"),
        zaxis=dict(title="Nombre de commits", gridcolor="gray", zerolinecolor="white"),
    ),
    font=dict(family="Arial", size=12, color="white"),  # Texte blanc pour lisibilité
)

# 📌 Enregistrement des fichiers
try:
    output_dir1 = "../../Images/Graph/"
    os.makedirs(output_dir1, exist_ok=True)
    fig.write_image(os.path.join(output_dir1, "commit_graph.png"))
except Exception as e:
    print("Erreur :", e)

try:
    output_dir2 = "../../"
    os.makedirs(output_dir2, exist_ok=True)
    fig.write_html(os.path.join(output_dir2, "index.html"))
except Exception as e:
    print("Erreur :", e)

print("✅ Graphique amélioré généré : commit_graph.png et index.html")