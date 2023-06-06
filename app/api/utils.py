import random
import os
from libs.lib_manejo_csv import lee_csv

def get_random_color():
    r1 = random.randint(0, 255)
    r2 = random.randint(0, 255)
    r3 = random.randint(0, 255)
    return '#%02X%02X%02X' % (r1, r2, r3)

def get_complex_protein_color():
    return '#%02X%02X%02X' % (255, 0, 0)

def generate_random_styles():
    _style = {
        "width": "mapData(score, 0, 0.006769776522008331, 20, 60)",
        "height": "mapData(score, 0, 0.006769776522008331, 20, 60)",
        "content": "data(name)",
        "font-size": "12px",
        "text-valign": "center",
        "text-halign": "center",
        "background-color": get_random_color(),
        "text-outline-color": "#555",
        "text-outline-width": "2px",
        "color": "#fff",
        "overlay-padding": "6px",
        "z-index": "10"
    }
    return _style

def execute_cluster_one(command: str, params: dict = None, file_name: str = None):
    if params:
        command = command + " " + " ".join([f"{k} {v}" for k, v in params.items()])
    print(command)
    os.system(command)
    if file_name:
        response = lee_csv(file_name)
        os.system(f"mv {file_name} /app/app/media/clusters/{file_name}")
        return response
    else:
        response = lee_csv("complex_cluster_response.csv")
        os.system("mv complex_cluster_response.csv /app/app/media/clusters/complex_cluster_response.csv")
    return response

def save_user_ppi(file):
    pass