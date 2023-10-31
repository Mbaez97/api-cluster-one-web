#!/usr/bin/env python
"""
Downloads a snapshot of the data input files (PPI + sequences + other stuff)
which will to be used for prediction.
"""

import os
import gzip
import sys
import datetime
import time
import logging
import urllib.request
import shutil
import requests  # type: ignore
import json


class DownloadSnapshot:
    """
    Class to download and store protein interaction data from various sources.
    """

    def __init__(self, snapshot_subdirectory, overwrite=False):
        """
        Initializes the DownloadSnapshot object.

        Args:
        - snapshot_subdirectory (str): Path to the directory where the downloaded files will be stored.
        - overwrite (bool): If True, overwrite existing files with the same name. Default is False.
        """
        self.snapshot_subdirectory = snapshot_subdirectory
        self.overwrite = overwrite

    def create_snapshot_subdirectory(self):
        """
        Creates the snapshot subdirectory if it does not exist.
        """
        if not os.path.exists(self.snapshot_subdirectory):
            os.makedirs(self.snapshot_subdirectory)

    def download_proteomes(self):
        out = open(os.path.join(self.snapshot_subdirectory, "proteomes.tab"), "w")
        requestURL = "https://www.ebi.ac.uk/proteins/api/proteomes?offset=0&size=-1&is_redundant=false"
        r = requests.get(requestURL, headers={"Accept": "application/json"})

        if not r.ok:
            r.raise_for_status()
            sys.exit()

        responseBody = json.loads(r.text)

        columns = [
            "upid",
            "name",
            "strain",
            "taxonomy",
            "sourceTaxonomy",
            "superregnum",
        ]

        zero_proteomes = set()

        total = len(responseBody)
        for i, p in enumerate(responseBody):
            d = {}
            for c in columns:
                try:
                    d[c] = p[c]
                except KeyError:
                    d[c] = "none"
            # retrieve proteins for this proteome
            requestURL = (
                "https://www.ebi.ac.uk/proteins/api/proteomes/proteins/{upid}".format(
                    upid=p["upid"]
                )
            )
            prots_r = requests.get(requestURL, headers={"Accept": "application/json"})
            if not prots_r.ok:
                prots_r.raise_for_status()
                sys.exit()
            prots_responseBody = json.loads(prots_r.text)
            proteins = set()
            for component in prots_responseBody["component"]:
                try:
                    for prot in component["protein"]:
                        proteins.add(prot["accession"])
                except KeyError:
                    zero_proteomes.add(p["upid"])
            d["prots"] = ",".join(proteins)
            out.write(
                "{upid}\t{name}\t{strain}\t{taxonomy}\t{sourceTaxonomy}\t{superregnum}\t{prots}\n".format(
                    **d
                )
            )
            print(
                "\r{i}/{total} ({perc:.2f}%)".format(
                    i=i, total=total, perc=(i / total)
                ),
                end="",
            )
        out.close()
        print()

    def download_uniprot_goa(self):
        url = (
            "ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/UNIPROT/" "goa_uniprot_all.gaf.gz"
        )
        local_file_name = "uniprot_goa.gz"
        local_uncompressed_data = os.path.join(
            self.snapshot_subdirectory, "uniprot_goa.tab"
        )
        if not os.path.isfile(local_uncompressed_data) or self.overwrite:
            local_compressed_data = self.__download_file(url, local_file_name)
            self.__gunzip_file(local_compressed_data, local_uncompressed_data)

    def download_gene_ontology(self):
        url = "http://geneontology.org/ontology/go-basic.obo"
        local_file_name = "go-basic.obo"
        self.__download_file(url, local_file_name)

    def download_uniprot_mapping(self):
        """
        Downloads the mapping between various protein ID types and UniProt IDs.
        """
        url = (
            "ftp://ftp.uniprot.org/pub/databases/uniprot/"
            "current_release/knowledgebase/idmapping/"
            "idmapping_selected.tab.gz"
        )
        local_file_name = "idmapping_selected.tab.gz"
        local_uncompressed_data = os.path.join(
            self.snapshot_subdirectory, "idmapping_selected.tab"
        )
        if not os.path.isfile(local_uncompressed_data) or self.overwrite:
            local_compressed_data = self.__download_file(url, local_file_name)
            self.__gunzip_file(local_compressed_data, local_uncompressed_data)

    @staticmethod
    def __gunzip_file(
        full_path_gzip_file, full_path_uncompressed_file, remove=True
    ):  # noqa
        """Gunzips a text file given its `full_path_gzip_file` into the
        `full_path_uncompressed_file`. If `remove` is True, the compressed
        file will be removed, as well.
        """
        with open(full_path_uncompressed_file, "wb") as out:
            with gzip.open(full_path_gzip_file) as f_in:
                shutil.copyfileobj(f_in, out)
        if remove:
            os.remove(full_path_gzip_file)

    def __download_file(self, url, localfile):
        """Downloads the file pointed by `url` into a file named `localfile`.
        The full path for downloading the file is constructed by prepending
        the snapshot subdirectory to the local file.
        This full path is returned.
        """
        CHUNK = 512 * 1024
        full_path_file = os.path.join(self.snapshot_subdirectory, localfile)
        if os.path.isfile(full_path_file) and not self.overwrite:
            return full_path_file
        temp_file_name = full_path_file + ".tmp"
        response = urllib.request.urlopen(url)
        with open(temp_file_name, "wb") as fp:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                fp.write(chunk)
        os.rename(temp_file_name, full_path_file)
        return full_path_file


def main(args):
    if not os.path.exists(args.directory):
        print("ERROR: A directory you have given does not exist")
        print(__doc__)
    else:
        if args.snapshot_directory is None:
            snapshot_subdirectory = os.path.join(
                args.directory,
                datetime.datetime.fromtimestamp(time.time()).strftime(
                    "%Y_%m_%d"
                ),  # noqa
            )
        else:
            snapshot_subdirectory = os.path.join(
                args.directory, args.snapshot_directory
            )

        download_snapshot = DownloadSnapshot(
            snapshot_subdirectory,
            overwrite=args.overwrite,
        )
        logger = logging.getLogger("download_snapshot")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S",  # noqa
        )
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # GOA = Gene Ontology Annotation
        # For each protein in UniProt, there is a GOA entry
        logger.info("downloading UniProtKB-GOA file")
        download_snapshot.download_uniprot_goa()

        logger.info("downloading Gene Ontology file")
        download_snapshot.download_gene_ontology()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="downloads a snapshot "
        + "with all available protein interaction datasets"
    )
    parser.add_argument(
        "directory",
        help="parent directory where the snapshot"
        + " directory will be placed",  # noqa
    )
    parser.add_argument(
        "--snapshot-directory",
        "-s",
        help="directory which "
        + "will be appended to the parent directory to make the full path for "
        + "the snapshot. If not given, a timestamp will be used instead",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        help="by default, files in the "
        + "snapshot folder will not be overwritten, allowing the continuation "
        + "of a failed download. If this flag is set, files will be "
        + "overwritten",
        action="store_true",
    )
    args = parser.parse_args()
    main(args)
