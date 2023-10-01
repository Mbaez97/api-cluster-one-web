import json
import requests  # type: ignore
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))

from app.crud import cluster_graph as crud_complex  # noqa
from app.db.session import SessionLocal  # noqa

from config import Settings  # noqa

settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)

ENRICHR_BASE_URL = "https://maayanlab.cloud/Enrichr/"

# Functions


def parse_complex_to_enrichr(db, complex: int):
    complex = crud_complex.get_proteins_by_cluster(db, id=complex)  # type: ignore # noqa
    complex = [str(protein.name) for protein in complex]  # type: ignore
    complex = "\n".join(complex)
    print(complex)
    return complex


def add_list(genes_str: list, description: str):
    """
    Add list gene or protein complex to enrichr
    Return: dict
        {
            "userListId": 1234567,
            "shortId": "abcd1",
        }
    """
    url = ENRICHR_BASE_URL + "addList"
    payload = {"list": genes_str, "description": (None, description)}
    response = requests.post(url, json=payload)
    if not response.ok:
        print(response.status_code)
        raise Exception("Error adding gene list")
    data = json.loads(response.text)
    return data


def view_added_gene_set(user_list_id: int):
    """
    View added gene set
    Return: dict
        {
            "genes": [
                "PHF14", "RBM3", "MSL1", "PHF21A", "ARL10", "INSR", "JADE2",
                "P2RX7", "LINC00662", "CCDC101", "PPM1B", "KANSL1L", "CRYZL1",
                "ANAPC16", "TMCC1", "CDH8", "RBM11", "CNPY2", "HSPA1L", "CUL2",
                "PLBD2", "LARP7", "TECPR2", "ZNF302", "CUX1", "MOB2", "CYTH2",
                "SEC22C", "EIF4E3", "ROBO2", "ADAMTS9-AS2", "CXXC1", "LINC01314", # noqa
                "ATF7", "ATP5F1"
            ],
            "description": "Example gene list"
        }
    """
    url = ENRICHR_BASE_URL + "view?userListId=" + str(user_list_id)
    response = requests.get(url)
    if not response.ok:
        raise Exception("Error getting gene list")
    data = json.loads(response.text)
    return data


def enrich_complex(user_list_id: int, gene_set_library: str):
    """
    Enrich complex
    Return: dict
        {
            "KEGG_2015": [
                [
                    1,
                    "ubiquitin mediated proteolysis",
                    0.06146387620182772,
                    -1.8593425456520887,
                    2.8168673182384705,
                    ["CUL2"],
                    0.21981251622012696
                ],
                [
                    2,
                    "type ii diabetes mellitus",
                    0.06594375486603808,
                    -1.799654722223511,
                    2.7264414418952905,
                    ["INSR"],
                    0.21981251622012696
                ],
                ...
            ]
        }
    """
    url = ENRICHR_BASE_URL + "enrich"
    query_string = (
        "?userListId="
        + str(user_list_id)
        + "&backgroundType="
        + gene_set_library  # noqa
    )
    response = requests.get(url + query_string)
    if not response.ok:
        raise Exception("Error fetching enrichment results")
    data = json.loads(response.text)
    return data


def execute_enrichment_complex(db, complex: int, gene_set_library: str):
    _complex = parse_complex_to_enrichr(db, complex)  # type: ignore
    description = f"Complex {complex} -> gene list"
    user_list_id = add_list(_complex, description)  # type: ignore # noqa
    enrich = enrich_complex(user_list_id, gene_set_library)
    return enrich


# Main
if __name__ == "__main__":
    # Get all clusters
    db = SessionLocal()
    test_cluster = 25005
    gene_set_libraries = [
        "GO_Biological_Process_2023",
        "GO_Cellular_Component_2023",
        "GO_Molecular_Function_2023",
    ]
    for gene_set_library in gene_set_libraries:
        enrich = execute_enrichment_complex(db, test_cluster, gene_set_library)
        print(enrich)
        print("========================================")
    db.close()
