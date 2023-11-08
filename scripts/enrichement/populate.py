import sys
import requests  # noqa
import json
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../../"))

from app.crud import cluster_graph, enrichment, go_terms  # noqa
from app.db.session import SessionLocal  # noqa

from config import Settings  # noqa
from libs.lib_manejo_csv import lee_csv  # noqa


settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)


def get_go_data(go_id: str):
    requestURL = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_id}"  # type: ignore # noqa

    r = requests.get(requestURL, headers={"Accept": "application/json"})

    if not r.ok:
        return None

    responseBody = json.loads(r.text)
    return responseBody


DOMAINS = {
    "biological_process": "BP",
    "cellular_component": "CC",
    "molecular_function": "MF",
}


def populate_from_file(
    file_path_enrichment_input: str, file_path_cluster_enrichment_output: str
):
    """
    Populates the database with data from two CSV files: one containing cluster data and the other containing
    enrichment data. The function reads the CSV files, creates clusters and go_terms, and associates them with
    each other in the database.

    Args:
        file_path_enrichment_input (str): The path to the CSV file containing the enrichment data.
        file_path_cluster_enrichment_output (str): The path to the CSV file containing the cluster data.

    Returns:
        str: A string indicating that the function has completed successfully.
    """
    db = SessionLocal()
    print("LOGS: Parse data from file to create cluster")
    _clusters_inputs_enrichment = lee_csv(file_path_enrichment_input)
    _clusters_outputs_enrichment = lee_csv(file_path_cluster_enrichment_output)
    print(file_path_enrichment_input)
    print(file_path_cluster_enrichment_output)
    for _cluster_input in _clusters_inputs_enrichment:
        _file_id = int(_cluster_input[0])
        _size = _cluster_input[1]
        _density = _cluster_input[2]
        _internal_weight = _cluster_input[3]
        _external_weight = _cluster_input[4]
        _quality = _cluster_input[5]
        _pvalue = _cluster_input[6]
        _elements = _cluster_input[7].split(" ")
        _obj = {
            "file_id": _file_id,
            "size": _size,
            "density": _density,
            "internal_weight": _internal_weight,
            "external_weight": _external_weight,
            "quality": _quality,
            "p_value": _pvalue,
            "elements": _elements,
            "cluster_one_log_params_id": 16,
        }
        _cluster = cluster_graph.get_cluster_by_elements(db, obj=_obj)
        print(f"LOGS: Parse data from file to create cluster: {_cluster.id}")
        cluster_graph.update(db, db_obj=_cluster, obj_in={"data_file_id": _file_id})  # type: ignore # noqa
        _go_terms_fields = []
        print("LOGS: Parse data from file to create go_terms")
        for _enrichment in _clusters_outputs_enrichment:
            _enrichment_data = _enrichment[0].split("\t")
            _file_id_cluster_file = int(_enrichment_data[0])
            _go_term = _enrichment_data[1]
            _p_value = float(_enrichment_data[2])
            if _file_id_cluster_file == _file_id:
                _data = get_go_data(_go_term)
                if _data is None:
                    continue
                _go_terms_fields.append(
                    {
                        "go_id": _go_term,
                        "p_value": _p_value,
                        "description": _data["results"][0]["definition"]["text"],  # type: ignore # noqa
                        "url_info": f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{_go_term}",  # type: ignore # noqa
                        "term": _data["results"][0]["name"],
                        "domain": DOMAINS[_data["results"][0]["aspect"]],
                    }
                )
        for _go_term_field in _go_terms_fields:
            _go_term = go_terms.get_by_go_id(db, go_id=_go_term_field["go_id"])
            if _go_term is None:
                _go_term = go_terms.quick_creation(db, obj=_go_term_field)
            # _enrichment = enrichment.get_by_cluster_id(db, cluster_id=_cluster.id)  # type: ignore # noqa
            # if _enrichment is None:
            _enrichment = enrichment.quick_creation(
                db,
                obj={
                    "p_value": _go_term_field["p_value"],
                    "notes": "Automatically created from file",
                    "state": 3,
                    "go_terms_id": _go_term.id,
                    "cluster_graph_id": _cluster.id,
                },
            )
        print("Enrichment created")
    db.close()
    return "Done"


if __name__ == "__main__":
    populate_from_file(
        "./enrichment_inputs/cluster_biogrid.csv",
        "./enrichment_outputs/UP000002311_559292_biogrid.overrep",
    )
