import sys
import random
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))

from libs.lib_manejo_csv import lee_csv, lee_txt  # noqa
from app.models import PPIGraph, Layout  # noqa
from app.crud import (  # noqa
    protein as crud_protein,
    edge as crud_edge,
    ppi_graph as crud_ppi,
)  # noqa
from app.db.session import SessionLocal  # noqa

from config import Settings  # noqa

settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)


def get_random_color():
    r1 = random.randint(0, 255)
    r2 = random.randint(0, 255)
    r3 = random.randint(0, 255)
    return "#%02X%02X%02X" % (r1, r2, r3)


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


def create_ppi(file_path: str):
    ppi_dataset = lee_txt(file_path)
    db = SessionLocal()
    _random_layout = db.query(Layout).filter(Layout.name == "random").first()
    _data = {
        "external_weight": 0,
        "internal_weight": 0,
        "density": 0,
        "size": len(ppi_dataset),
        "quality": 0,
        "layout": _random_layout,
        "data": file_path,
        "name": file_path.replace("./app/media/ppi/", ""),
        "preloaded": False,
    }
    _new_ppi = crud_ppi.create_ppi_from_file(db, obj=_data)
    print(_new_ppi)


def crate_layouts():
    print("LOGS: Creating layouts")
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


def create_edge_ppi_interaction_by_ppi_id(file_path: str, ppi_id: int):
    ppi_dataset = lee_txt(file_path, delimiter="\t")
    db = SessionLocal()
    _ppi_objet = db.query(PPIGraph).filter(PPIGraph.id == ppi_id).first()
    for data in ppi_dataset:
        data = data.replace("\n", "")
        _data = data.split("\t")
        if len(_data) == 1:
            _data = data.split(" ")
        protein_1 = crud_protein.get_by_name(db, name=_data[0])
        protein_2 = crud_protein.get_by_name(db, name=_data[1])
        try:
            _weight = float(_data[2])
        except Exception:
            _weight = 0.0
        if not protein_1:
            protein_1 = crud_protein.quick_creation(db, name=_data[0])
        if not protein_2:
            protein_2 = crud_protein.quick_creation(db, name=_data[1])
        _edge = crud_edge.get_by_proteins(
            db, protein_a_id=protein_1.id, protein_b_id=protein_2.id
        )
        if _edge:
            _obj = {
                "id": _edge.id,
                "refers_to": _ppi_objet,
                "weight": _weight,
            }
            crud_edge.add_edge_to_ppi(db, obj=_obj)
        else:
            _obj = {
                "protein_a_id": protein_1.id,
                "protein_b_id": protein_2.id,
                "weight": _weight,
                "refers_to": _ppi_objet,
                "direction": 0,
            }
            crud_edge.create_edge_for_ppi(db, obj=_obj)


def parse_ppi_csv_to_txt(
    file_path: str, file_out_path: str, wieght: bool = False
):  # noqa
    ppi_dataset = lee_csv(file_path, delimiter=",")
    with open(file_out_path, "w") as f:
        print("LOGS: Creating file")
        for data in ppi_dataset:
            print(data)
            if wieght:
                f.write(f"{data[0]}\t{data[1]}\t{data[2]}\n")
            else:
                f.write(f"{data[0]}\t{data[1]}\n")
    print("LOGS: File created")


def parse_ppi_file_hq_to_txt(
    file_path: str, file_out_path: str, wieght: bool = False
):  # noqa
    ppi_dataset = lee_txt(file_path)
    with open(file_out_path, "w") as f:
        print("LOGS: Creating file")
        for i, data in enumerate(ppi_dataset):
            # breakpoint()
            _data = data.split("\t")
            print(_data)
            if i == 0:
                continue
            if wieght:
                f.write(f"{_data[0]}\t{_data[1]}\t{_data[2]}\n")
            else:
                f.write(f"{_data[0]}\t{_data[1]}\n")
    print("LOGS: File created")


if __name__ == "__main__":
    print("LOGS: Running script")
    # Create PPI from file for the first time, we use this scripts for testing
    # crate_layouts()
    # create_ppi("./app/media/ppi/PP-Pathways_ppi.txt")

    # Parse PPI file from csv to txt or from hq to txt
    # parse_ppi_csv_to_txt(
    #     "./app/media/ppi/PP-Pathways_ppi.csv",
    #     "./app/media/ppi/PP-Pathways_ppi.txt",
    #     wieght=True,
    # )
    parse_ppi_file_hq_to_txt(
        "./dataset_test_performance/hq_file/OryzaSativa_binary_hq.txt",
        "./dataset_test_performance/parsed/OryzaSativa_binary.txt",
    )
