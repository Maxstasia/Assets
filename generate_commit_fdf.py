# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_commit_fdf.py                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/02/26 12:32:07 by mstasiak          #+#    #+#              #
#    Updated: 2025/02/27 16:20:28 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import numpy as np
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
    plot_wireframe(X, Y, Z)
