# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    generate_cube.py                                   :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mstasiak <mstasiak@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/03/03 13:06:43 by mstasiak          #+#    #+#              #
#    Updated: 2025/03/03 16:46:11 by mstasiak         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import numpy as np
from PIL import Image, ImageDraw
import os

# Paramètres du GIF
size = 300  # Taille de l'image
frames = 60  # Nombre d'images
cube_size = 80  # Taille du cube
output_dir = "../../Images/Cube"
# Vérifie si le dossier existe
if not os.path.exists(output_dir):
    print(f"📁 Création du dossier de sortie : {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

# Vérifie les permissions
if not os.access(output_dir, os.W_OK):
    raise PermissionError(f"❌ Erreur : Pas de permission d'écriture dans {output_dir}")

gif_name = os.path.join(output_dir, "cube_rotation.gif")

def rotate_3d(points, angle_x, angle_y, angle_z):
    """Applique une rotation 3D aux points du cube."""
    rx = np.array([
        [1, 0, 0],
        [0, np.cos(angle_x), -np.sin(angle_x)],
        [0, np.sin(angle_x), np.cos(angle_x)]
    ])
    ry = np.array([
        [np.cos(angle_y), 0, np.sin(angle_y)],
        [0, 1, 0],
        [-np.sin(angle_y), 0, np.cos(angle_y)]
    ])
    rz = np.array([
        [np.cos(angle_z), -np.sin(angle_z), 0],
        [np.sin(angle_z), np.cos(angle_z), 0],
        [0, 0, 1]
    ])
    rotation_matrix = rx @ ry @ rz
    return np.dot(points, rotation_matrix.T)

def draw_cube(draw, rotated_points, color):
    """Dessine les arêtes du cube en reliant les points avec une couleur donnée."""
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # Face avant
        (4, 5), (5, 7), (7, 6), (6, 4),  # Face arrière
        (0, 4), (1, 5), (2, 6), (3, 7)   # Arêtes entre faces
    ]
    for start, end in edges:
        x1, y1 = rotated_points[start][:2]
        x2, y2 = rotated_points[end][:2]
        draw.line([x1, y1, x2, y2], fill=color, width=3)

# Coordonnées du cube centré
cube_points = np.array([
    [-1, -1, -1], [1, -1, -1], [-1, 1, -1], [1, 1, -1],  # Face avant
    [-1, -1, 1], [1, -1, 1], [-1, 1, 1], [1, 1, 1]       # Face arrière
]) * (cube_size // 2)

images = []

# Génération des images du GIF
for i in range(frames):
    angle_x = i * (2 * np.pi / frames)
    angle_y = i * (2 * np.pi / frames)
    angle_z = i * (2 * np.pi / frames)

    rotated = rotate_3d(cube_points, angle_x, angle_y, angle_z)
    projected = rotated[:, :2] + size // 2  # Projection simple

    # Génération d'une couleur dynamique (RGB)
    r = int(127 * (1 + np.sin(i * 2 * np.pi / frames)))
    g = int(127 * (1 + np.sin(i * 2 * np.pi / frames + 2)))
    b = int(127 * (1 + np.sin(i * 2 * np.pi / frames + 4)))
    color = (r, g, b)

    img = Image.new("RGB", (size, size), "black")
    draw = ImageDraw.Draw(img)
    draw_cube(draw, projected, color)
    images.append(img)

# Sauvegarde en GIF
try:
    images[0].save(gif_name, save_all=True, append_images=images[1:], duration=50, loop=0)
except Exception as e:
    print(f"❌ Erreur lors de la création du fichier : {e}")

print(f"✅ GIF généré ici : {gif_name}")
