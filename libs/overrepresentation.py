import scipy.stats as stats  # type: ignore
import pandas as pd  # type: ignore
import logging
import requests  # type: ignore
import json
import time
from rich.progress import track  # type: ignore
from libs.golib.core.gene_ontology import GeneOntology  # type: ignore
from libs.lib_manejo_csv import lee_csv  # noqa
from app.crud import cluster_graph, enrichment, go_terms  # noqa
from app.db.session import SessionLocal  # noqa

from config import Settings  # noqa

settings = Settings()
print(settings.SQLALCHEMY_DATABASE_URI)


logger = logging.getLogger("overrepresentation")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


def read_complexes(path, max_group_size):
    complexes = {}
    with open(path) as f:
        for line in f:
            if not line.startswith("Clu"):
                fields = line.strip().split(",")
                if int(fields[1]) <= max_group_size:
                    complexes[int(fields[0])] = (
                        fields[7].replace('"', "").split()
                    )  # noqa: E501
    return complexes


def get_proteins_from_gaf_file(path):
    """
    Only returns the proteins in the GAF file in version 2.2
    """
    proteins = []
    with open(path, "r") as f:
        for line in f:
            if line[0] == "!":
                continue
            fields = line.strip().split("\t")
            proteins.append(fields[2])
    return proteins


def get_proteins_in_complexes(complexes):
    proteins = set()
    for _, prots in complexes.items():
        proteins |= set(prots)
    return proteins


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


def run_ora(
    complexes_file,
    goa_file,
    obo_file,
    out_file,
    pvalue_tau=0.05,
    max_group_size=100,
):
    logger.info(f"Getting proteins of GAF file {goa_file}...")
    background = get_proteins_from_gaf_file(goa_file)
    total_background = len(background)
    logger.info(f"Found {total_background} proteins in the proteome")
    print(background[len(background) - 5 : len(background)])

    logger.info(f"Processing Complexes file {complexes_file}...")
    complexes = read_complexes(complexes_file, max_group_size)
    complexes_prots = get_proteins_in_complexes(complexes)
    num_complexes = len(complexes)
    print(complexes_prots[len(complexes_prots) - 5 : len(complexes_prots)])

    logger.info(f"Found {num_complexes} complexes")
    logger.info(f"Found {len(complexes_prots)} proteins in the complexes")
    time.sleep(5)

    logger.info("Building structure Ontology in memory...")
    go = GeneOntology(obo=obo_file)
    go.build_ontology()

    logger.info("Loading GO annotations for this organins...")
    go.load_gaf_file(goa_file, "overrep")
    go.up_propagate_annotations("overrep")
    annotations = go.annotations("overrep")
    print(annotations.head())

    logger.info("Building unified annotations matrix...")
    all_prots = set(background) | set(complexes_prots)
    print(all_prots[len(all_prots) - 5 : len(all_prots)])
    bg_cond = annotations["Protein"].isin(all_prots)

    table = (
        annotations[bg_cond]
        .pivot(index="GO ID", columns="Protein", values="Score")
        .fillna(0.0)
    )
    table_prots = table.columns.values
    num_hypotheses = table.shape[0]

    # the background is shared for all complexes,
    # so we can pre-calculate the counts
    logger.info("Calculating background counts...")
    annotated_bg = list(set(background) & set(table_prots))
    print(annotated_bg[len(annotated_bg) - 5 : len(annotated_bg)])
    bg_counts = table[annotated_bg].sum(axis=1)
    # this is more than anything a sanity check, should not change the value
    bg_counts = bg_counts[bg_counts > 0]
    tot_minus_bg_counts = total_background - bg_counts

    logger.info(
        f"Found {num_complexes} complexes," " analyzing overrepresentation"
    )  # noqa
    overrepresented_goterms = []
    time.sleep(5)
    for i, (complex_id, proteins) in track(
        enumerate(complexes.items()),
        description="Analyzing...",
        total=num_complexes,  # noqa
    ):
        # Log progress
        perc = i / len(complexes)
        logger.info(
            f"Analyzing complex {i}/{len(complexes)}"
            f" ({perc * 100.0:.2f}%)) ..."  # noqa
        )

        logger.info(f"Complex {complex_id} has {len(proteins)} proteins")
        # Calculate the counts for this group
        total_group = len(proteins)
        annotated_gr_prots = list(set(proteins) & set(table_prots))
        group_counts = table[annotated_gr_prots].sum(axis=1)
        group_counts_idx = group_counts > 0
        group_counts = group_counts[group_counts_idx]
        if group_counts.shape[0] < 1:
            continue
        counts = pd.concat(
            [
                group_counts,
                bg_counts[group_counts_idx],
                total_group - group_counts,
                tot_minus_bg_counts[group_counts_idx],
            ],
            axis=1,
        ).reset_index()
        counts.columns = [
            "GO ID",
            "group_count",
            "bg_count",
            "gr_tot-gr_count",
            "bg_tot-bg_count",
        ]
        # calculate the pvalues
        counts["pvalue"] = counts.apply(
            lambda x: stats.fisher_exact(
                table=[
                    [x["group_count"], x["bg_count"]],
                    [x["gr_tot-gr_count"], x["bg_tot-bg_count"]],
                ],
                alternative="greater",
            )[1],
            axis=1,
        )
        # correct pvalues with the Bonferroni correction
        counts["corrected_pvalue"] = counts["pvalue"] * num_hypotheses
        for _, r in counts[counts["corrected_pvalue"] < pvalue_tau].iterrows():
            overrepresented_goterms.append(
                (complex_id, r["GO ID"], r["corrected_pvalue"])
            )

    logger.info("Writing overrepresentation file...")
    with open(out_file, "w") as out:
        for complex_id, goterm, pvalue in overrepresented_goterms:
            out.write(f"{complex_id}\t{goterm}\t{pvalue}\n")

    logger.info("Populate db...")
    populate_from_file(
        complexes_file,
        out_file,
    )

    return True
