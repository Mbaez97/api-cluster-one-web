import random
import os

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

def execute_cluster_one(command: str, params: dict = None):
    if params:
        command = command + " " + " ".join([f"{k} {v}" for k, v in params.items()])
    print(command)
    os.system(command)
    with open("complex_cluster_response.txt", "r") as f:
        response = f.read()
    os.system("rm complex_cluster_response.txt")
    return response.split("\n")