# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_graph.py                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/02/27 15:27:19 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import subprocess
import pandas as pd
import plotly.express as px

# 1️⃣ Récupérer l'historique des commits
def get_commit_history():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H %cd", "--date=format:%Y-%m-%d"],
        capture_output=True,
        text=True,
    )
    commits = [line.split() for line in result.stdout.split("\n") if line]
    return [(commit[0], commit[1]) for commit in commits]

# 2️⃣ Transformer les données en DataFrame
commits = get_commit_history()
df = pd.DataFrame(commits, columns=["hash", "date"])
df["date"] = pd.to_datetime(df["date"])
df["count"] = df.groupby("date")["date"].transform("count")
df = df.drop_duplicates(subset=["date"])

# 3️⃣ Générer un graphique interactif
fig = px.scatter_3d(
    df,
    x=df["date"].dt.day,
    y=df["date"].dt.month,
    z=df["count"],
    color=df["count"],
    size=df["count"],
    hover_name=df["date"].dt.strftime("%Y-%m-%d"),
    labels={"x": "Jour", "y": "Mois", "z": "Nombre de commits"},
    title="Historique des Commits (3D)",
)

# 4️⃣ Sauvegarde des fichiers
fig.write_image("commit_graph.png")
fig.write_html("commit_graph.html")

print("✅ Graphique généré : commit_graph.png et commit_graph.html")

""" import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime
import subprocess

def get_commit_counts():
    # Récupère le nombre de commits du jour
    today = datetime.date.today().strftime('%Y-%m-%d')
    result = subprocess.run([
        'git', 'rev-list', '--count', f'--since={today} 00:00', f'--until={today} 23:59', 'HEAD'
    ], capture_output=True, text=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0

def generate_wireframe_grid(size=10, commit_multiplier=1):
    X = np.linspace(-5, 5, size)
    Y = np.linspace(-5, 5, size)
    X, Y = np.meshgrid(X, Y)
    Z = np.sin(X) * np.cos(Y) * commit_multiplier  # Variation en fonction du nombre de commits
    return X, Y, Z

def plot_wireframe(X, Y, Z, filename="commit_graph.png"):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Définir le fond en noir
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")

    # Désactiver les plans de fond
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.grid(False)
    
    ax.plot_wireframe(X, Y, Z, color='#00FF00')  # Fil de fer vert
    
    # Sauvegarde en fichier PNG au lieu d'afficher
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor="black")
    plt.close(fig)  # Fermer la figure pour éviter les fuites mémoire

if __name__ == "__main__":
    commit_count = get_commit_counts()
    X, Y, Z = generate_wireframe_grid(size=30, commit_multiplier=commit_count)
    plot_wireframe(X, Y, Z) """
