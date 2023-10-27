#!/usr/bin/env python
"""
Downloads a snapshot of the data input files (PPI + sequences + other stuff)
which will to be used for prediction.
"""

import os
import zipfile
import gzip
import sys
import datetime
import time
import logging
import urllib.request
import shutil
import tarfile
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

    def download_swissprot(self):
        """
        Downloads the Swiss-Prot protein sequence data.
        """
        url = (
            "ftp://ftp.uniprot.org/pub/databases/uniprot/"
            "current_release/knowledgebase/complete/"
            "uniprot_sprot.fasta.gz"
        )
        local_file_name = "swissprot.gz"
        local_uncompressed_data = os.path.join(
            self.snapshot_subdirectory, "swissprot.fasta"
        )
        if not os.path.isfile(local_uncompressed_data) or self.overwrite:
            local_compressed_data = self.__download_file(url, local_file_name)
            self.__gunzip_file(local_compressed_data, local_uncompressed_data)

    def download_trembl(self):
        """
        Downloads the TrEMBL protein sequence data.
        """
        url = (
            "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/"
            "knowledgebase/complete/uniprot_trembl.fasta.gz"
        )
        local_file_name = "trembl.gz"
        local_uncompressed_data = os.path.join(
            self.snapshot_subdirectory, "trembl.fasta"
        )
        if not os.path.isfile(local_uncompressed_data) or self.overwrite:
            local_compressed_data = self.__download_file(url, local_file_name)
            self.__gunzip_file(local_compressed_data, local_uncompressed_data)

    def download_species_list(self):
        """
        Downloads the list of species available in UniProt.
        """
        url = (
            "ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/"
            "knowledgebase/complete/docs/speclist.txt"
        )
        local_file_name = "species_list.txt"
        self.__download_file(url, local_file_name)

    def download_organism_info(self):
        # TODO: implement a version with pagination
        url = "https://rest.uniprot.org/taxonomy/stream?compressed=true&fields=id%2Ccommon_name%2Cscientific_name%2Clineage%2Cparent&format=tsv&query=%28%2A%29"
        local_compressed_data = os.path.join(
            self.snapshot_subdirectory, "org_info.tab.gz"
        )
        local_uncompressed_data = os.path.join(
            self.snapshot_subdirectory, "org_info.tab"
        )
        if not os.path.exists(local_uncompressed_data) or self.overwrite:
            with requests.get(url, stream=True) as request:
                request.raise_for_status()
                with open(local_compressed_data, "wb") as f:
                    for chunk in request.iter_content(chunk_size=2**20):
                        f.write(chunk)
            self.__gunzip_file(local_compressed_data, local_uncompressed_data)

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

    def download_taxonomy_dump(self):
        url = "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
        local_file_name = "taxdump.tar.gz"
        local_uncompressed_data = os.path.join(self.snapshot_subdirectory, "names.dmp")
        if not os.path.isfile(local_uncompressed_data) or self.overwrite:
            local_compressed_data = self.__download_file(url, local_file_name)
            self.__untargz_target(
                local_compressed_data, local_uncompressed_data, "names.dmp"
            )

    @staticmethod
    def __unzip_file(
        full_path_zip_file, file_name, full_path_uncompressed_file, remove=True
    ):
        """Unzips a text file given its `full_path_zip_file` into the
        `full_path_uncompressed_file`.
        Only the `file_name` will be uncompressed. If `remove` is
        True, the compressed file will be removed afterwards.
        """
        with open(full_path_zip_file, "rb") as fh:
            z = zipfile.ZipFile(fh)
            outpath = os.path.dirname(full_path_uncompressed_file)
            for name in z.namelist():
                if file_name not in name:
                    continue
                z.extract(name, outpath)
                full_new_name = os.path.join(outpath, name)
                if full_new_name != full_path_uncompressed_file:
                    os.rename(full_new_name, full_path_uncompressed_file)
        if remove:
            os.remove(full_path_zip_file)

    @staticmethod
    def __untargz_target(
        full_path_targz_file, full_path_uncompressed_file, target_file, remove=True
    ):
        """Extracts the =`target_file` from the `full_path_targz_file`
        tar.gz provided into `full_path_uncompressed_file`. If `remove` is
        True, the compressed file will be removed, as well.
        """
        # from http://stackoverflow.com/a/37753786/943138
        with tarfile.open(full_path_targz_file, "r|*") as tar:
            counter = 0
            for member in tar:
                if member.isfile():
                    filename = os.path.basename(member.name)
                    if filename != target_file:  # do your check
                        continue
                    with open(full_path_uncompressed_file, "wb") as output:
                        shutil.copyfileobj(tar.fileobj, output, member.size)
                    break  # got our file
                counter += 1
                if counter % 1000 == 0:
                    tar.members = []  # free ram... yes we have to do this manually
            tar.members = []  # free ram... yes we have to do this manually
        if remove:
            os.remove(full_path_zip_file)

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

    def download_taxonomy(self):
        """Downloads the taxonomy data from NCBI"""
        taxdump = os.path.join(self.snapshot_subdirectory, "taxdump.tar.gz")
        urllib.request.urlretrieve(
            "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz", taxdump
        )
        taxcat = os.path.join(self.snapshot_subdirectory, "taxcat.tar.gz")
        urllib.request.urlretrieve(
            "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxcat.tar.gz", taxcat
        )
        taxo_dir = os.path.join(self.snapshot_subdirectory, "taxonomy")
        if not os.path.exists(taxo_dir):
            os.makedirs(taxo_dir)

        import tarfile

        ttaxdump = tarfile.open(taxdump, "r:gz")
        ttaxdump.extractall(taxo_dir)
        ttaxcat = tarfile.open(taxcat, "r:gz")
        ttaxcat.extractall(taxo_dir)
        os.remove(taxdump)
        os.remove(taxcat)


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
            args.dip_user,
            args.dip_pass,
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

        logger.info("downloading proteomes")
        download_snapshot.download_proteomes()


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
