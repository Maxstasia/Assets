# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_graph.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/02/27 16:24:38 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import subprocess
import pandas as pd
import plotly.express as px
import datetime as dt

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
df["day_of_week"] = df["date"].dt.weekday      # Jour de la semaine (0=Lundi, 6=Dimanche)

# 🔥 Correction : Comptage des commits par (semaine, jour)
df_count = df.groupby(["week", "day_of_week"]).size().reset_index(name="count")

# 🔥 Correction : Ajouter les jours manquants avec un count = 0
weeks = range(df["week"].min(), df["week"].max() + 1)
days = range(7)
full_index = pd.MultiIndex.from_product([weeks, days], names=["week", "day_of_week"])
df_count = df_count.set_index(["week", "day_of_week"]).reindex(full_index, fill_value=0).reset_index()

# 3️⃣ Générer un graphique interactif en 3D
fig = px.scatter_3d(
    df_count,
    x="week",  # Semaine de l'année
    y="day_of_week",  # Jour de la semaine
    z="count",  # Nombre de commits
    color="count",
    size="count",
    hover_name=df_count["week"].astype(str) + "-W" + df_count["day_of_week"].astype(str),
    labels={"week": "Semaine", "day_of_week": "Jour de la semaine", "count": "Commits"},
    title="Historique des Commits sur 1 an (3D)"
)

# 4️⃣ Sauvegarde des fichiers
fig.write_image("commit_graph.png")
fig.write_html("commit_graph.html")

print("✅ Graphique généré : commit_graph.png et commit_graph.html")
