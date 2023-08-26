import sys
import requests
import random
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))

from libs.lib_manejo_csv import lee_csv, lee_txt
from app.models import Protein, Style, Edge, PPIGraph, Layout
from app.db.session import SessionLocal

from config import Settings

settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)


def get_random_color():
    r1 = random.randint(0, 255)
    r2 = random.randint(0, 255)
    r3 = random.randint(0, 255)
    return "#%02X%02X%02X" % (r1, r2, r3)


def get_complex_protein_color():
    return "#%02X%02X%02X" % (255, 0, 0)


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
        "z-index": "10",
    }
    return _style


def crate_protein_by_ppi(file_path: str):
    """
    Crea los nodos de proteinas a partir de un archivo de PPI.
    """
    # Lee el archivo TXT
    dataset = lee_txt(file_path)
    _creados = []
    # Crea la sesion de la base de datos
    db = SessionLocal()
    for data in dataset:
        _data = data.split("\t")
        _url = "www.ebi.ac.uk/proteins/api/proteins/"
        # Crea el nodo de la proteina
        if _data[0] in _creados:
            continue
        _creados.append(_data[0])
        _style = generate_random_styles()
        _style_objet = Style(
            ccs_styles=_style,
            type=0,
        )
        db.add(_style_objet)

        protein_1 = Protein(
            name=_data[0],
            description="Automatic node created from PPI file",
            score=0.0,
            url_info=_url + _data[0],
            style=_style_objet,
        )
        db.add(protein_1)
        if _data[1] in _creados:
            continue
        _creados.append(_data[1])
        protein_2 = Protein(
            name=_data[1].replace("\n", ""),
            description="Automatic node created from PPI file",
            score=0.0,
            url_info=_url + _data[1],
            style=_style_objet,
        )
        db.add(protein_2)
        db.commit()
        print("Protein created: ", protein_1.name)
        print("Protein created: ", protein_2.name)
    db.close()


def create_ppi(file_path: str):
    ppi_dataset = lee_csv(file_path)
    db = SessionLocal()
    _get_random_layout = db.query(Layout).filter(Layout.name == "random").first()
    _ppi_objet = PPIGraph(
        name="PPI Biogrid Yeast Physical Unweighted",
        preloaded=True,
        size=len(ppi_dataset),
        density=0.0,
        layout=_get_random_layout,
    )
    db.add(_ppi_objet)
    db.commit()
    for data in ppi_dataset:
        _data = data[0].split("\t")
        protein_1 = db.query(Protein).filter(Protein.name == _data[0]).first()
        protein_2 = (
            db.query(Protein).filter(Protein.name == _data[1].replace("\n", "")).first()
        )
        _edge_style = {
            "selected": False,
            "selectable": True,
            "locked": False,
            "grabbable": False,
            "classes": "pp",
            "line-color": "#ccc",
            "target-arrow-color": "#ccc",
        }
        _edge_style_objet = Style(
            cytoscape_styles=_edge_style,
            type=1,
        )
        db.add(_edge_style_objet)
        _edge = Edge(
            protein_a=protein_1,
            protein_b=protein_2,
            weight=0.0,
            has_direction=False,
            direction=0,
            style=_edge_style_objet,
        )
        db.add(_edge)
        _ppi_objet.edge.append(_edge)
        db.commit()


def crate_layouts():
    layouts = [
        "cola",
        "cose",
        "cose-bilkent",
        "dagre",
        "fcose",
        "grid",
        "klay",
        "spread",
        "concentric",
        "breadthfirst",
        "circle",
        "concentric",
        "cose",
        "grid",
        "preset",
        "random",
    ]
    db = SessionLocal()
    for layout in layouts:
        _layout = Layout(
            name=layout,
            animated=True,
            node_spacing=10,
            randomize=True,
            max_simulation_time=4000,
        )
        db.add(_layout)
        db.commit()


create_ppi("ppi_biogrid_yeast_physical_unweighted.txt")
# crate_layouts()
