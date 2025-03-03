# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_graph.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/03/03 15:24:14 by mstasiak         ###   ########.fr        #
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

# 📌 Comptage des commits
df_count = df.groupby(["year", "week", "day_of_week", "repo"]).size().reset_index(name="count")

# 📌 Création du graphique avec liens cliquables
fig = px.scatter_3d(
    df_count,
    x="week",
    y="day_of_week",
    z="count",
    color="repo",
    size="count",
    hover_name=df_count["repo"] + " - " + df_count["year"].astype(str) + "-S" + df_count["week"].astype(str),
    labels={"week": "Semaine", "day_of_week": "Jour", "count": "Commits"},
    title="Historique des Commits GitHub (1 an)"
)

# 📌 Enregistrement du fichier
output_dir = "../../Images/Graph/"
os.makedirs(output_dir, exist_ok=True)  # Crée le dossier si inexistant
fig.write_image(os.path.join(output_dir, "commit_graph.png"))
fig.write_html(os.path.join(output_dir, "commit_graph.html"))

print("✅ Graphique généré : commit_graph.png et commit_graph.html")


""" import subprocess
import pandas as pd
import plotly.express as px
import datetime as dt
import os  # Ajout pour la gestion des dossiers

# 1️⃣ Récupérer l'historique des commits sur 1 an
def get_commit_history():
    result = subprocess.run(
        ["git", "log", "--since=1.year", "--pretty=format:%H %cd", "--date=format:%Y-%m-%d"],
        capture_output=True,
        text=True,
    )
    commits = [line.split() for line in result.stdout.split("\n") if line]
    return [(commit[0], commit[1]) for commit in commits]

# 2️⃣ Transformer les données en DataFrame
commits = get_commit_history()
df = pd.DataFrame(commits, columns=["hash", "date"])
df["date"] = pd.to_datetime(df["date"])
df["week"] = df["date"].dt.isocalendar().week  # Numéro de la semaine dans l'année
df["year"] = df["date"].dt.isocalendar().year  # Année pour éviter les bugs entre 2 ans
df["day_of_week"] = df["date"].dt.weekday      # Jour de la semaine (0=Lundi, 6=Dimanche)

# 🔥 Correction : Comptage des commits par (année, semaine, jour)
df_count = df.groupby(["year", "week", "day_of_week"]).size().reset_index(name="count")

# 🔥 Correction : Générer toutes les semaines et jours possibles
min_year, max_year = df["year"].min(), df["year"].max()
min_week, max_week = df["week"].min(), df["week"].max()

weeks = range(min_week, max_week + 1)
days = range(7)
years = range(min_year, max_year + 1)

full_index = pd.MultiIndex.from_product([years, weeks, days], names=["year", "week", "day_of_week"])
df_count = df_count.set_index(["year", "week", "day_of_week"]).reindex(full_index, fill_value=0).reset_index()

# 3️⃣ Générer un graphique interactif en 3D
fig = px.scatter_3d(
    df_count,
    x="week",  # Semaine de l'année
    y="day_of_week",  # Jour de la semaine
    z="count",  # Nombre de commits
    color="count",
    size="count",
    hover_name=df_count["year"].astype(str) + "-S" + df_count["week"].astype(str) + "-J" + df_count["day_of_week"].astype(str),
    labels={"week": "Semaine", "day_of_week": "Jour de la semaine", "count": "Commits"},
    title="Historique des Commits sur 1 an (3D)"
)

# 4️⃣ Vérification et création du dossier
output_dir = "../../Images/Graph/"
os.makedirs(output_dir, exist_ok=True)  # Crée le dossier si inexistant

print(df_count.tail(10))  # Affiche les 10 dernières lignes du DataFrame

# 5️⃣ Sauvegarde des fichiers
fig.write_image(os.path.join(output_dir, "commit_graph.png"))
fig.write_html(os.path.join(output_dir, "commit_graph.html"))

print("✅ Graphique généré : commit_graph.png et commit_graph.html") """
