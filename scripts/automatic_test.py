"""
On this file we want to simulate a normal use case.
 - Scientifics upload his/her PPI (CSV or TXT) and his/her GOA FILE.
 - Star cronomometer
 - Wait for a few minutes, then processing the PPI (Upload in Memory)
 - Execute ClusterONE WEB
 - Wait for the results, when the results are ready, execute ORA
 ---(Parallel of CLusterONE WEB API parses the results)---
 - Stop cronomometer
 - Start new cronomometer
 - Start loop where we wait for the ORA results
 ---(while we call ORA API every 10 seconds)---
 - Stop cronomometer
 - Write the results in a file

And also we want to plot the final file results in a graph
 - Read the results from the file
 ---(PPI, Time to cluster, Time to ORA, Total time)---
 - Plot the results
"""

import sys
import requests  # type: ignore
from pathlib import Path

import os
import time

HERE = Path(__file__).parent
sys.path.append(str(HERE / "../"))
print(HERE)
from libs.lib_manejo_csv import lee_csv, crea_csv, escribe_csv  # noqa


def open_binary_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return data


def main(do_ora=True):
    # Read all ppi files, i don't know how many files there are
    # PATH_TEST = "/Users/marcelobaez/Desarrollo Academico/paccanaro-lab/develop/api-cluster-one-web/dataset_test_performance/"  # noqa
    PATH_TEST = "/home/marcelo.baez/develop/api-cluster-one-web/dataset_test_performance/"  # noqa
    if os.path.exists(PATH_TEST):
        print("Path exists")
        crea_csv(
            "measures.csv", ["PPI", "Time to cluster", "Time to ORA", "Total time"]
        )
        # Get all ppi files name
        ppi_test_dir = PATH_TEST + "parsed/"
        ppi_files = os.listdir(ppi_test_dir)
        for ppi_file in ppi_files:
            start_time = time.time()
            # Step 1: Upload PPI
            print("STEP 1: Upload PPI")
            print(f"Executing for {ppi_file}")
            _file_ppi = open_binary_file(ppi_test_dir + ppi_file)
            files = {"file": (ppi_file, _file_ppi)}
            r = requests.post(
                "http://localhost:8203/v1/api/graph/ppi/",
                files=files,
                # headers={"Content-Type": "application/octet-stream"},
            )
            if r.status_code == 200:
                print("PPI uploaded")
                _ppi_json = r.json()
                print(_ppi_json)
            else:
                print(r.text)
                break

            if do_ora:
                # Step 2: Upload GOA
                print("STEP 2: Upload GOA")
                goa_path = PATH_TEST + "goa_file/"
                goa_files = os.listdir(goa_path)
                for goa_file in goa_files:
                    _goa_name_aux = goa_file.split(".")[0]
                    _ppi_name_aux = ppi_file.split(".")[0]
                    if _goa_name_aux == _ppi_name_aux:
                        print(f"Executing for {goa_file}")
                        _file_goa = open_binary_file(goa_path + goa_file)
                        files = {"file": (goa_file, _file_goa)}
                        r = requests.post(
                            "http://localhost:8203/v1/api/enrichment/upload/goa/",
                            files=files,
                        )
                        if r.status_code == 200:
                            print("GOA uploaded")
                            _goa_json = r.json()
                            print(_goa_json)
                            break
                        else:
                            print(r.text)
                            break

            # delay
            time.sleep(_ppi_json["size"] if _ppi_json["size"] > 0 else 30)
            # Step 3: Execute ClusterONE
            print("STEP 3: Execute ClusterONE")
            if do_ora:
                _url = f"http://localhost:8203/v1/api/cluster_one/run/?pp_id={_ppi_json['id']}&goa_file={_goa_json['goa_file']}"
            else:
                _url = f"http://localhost:8203/v1/api/cluster_one/run/?pp_id={_ppi_json['id']}"
            r = requests.post(
                _url,  # noqa
            )
            if r.status_code == 200:
                print("ClusterONE executed")
                _cluster_json = r.json()
                _cluster_to_test_ora = _cluster_json[0]["code"]
            else:
                print(r.text)
                break

            end_cluster_time = time.time()
            print(
                f"Time to cluster: {end_cluster_time - start_time:.4f} seconds"
            )  # noqa

            start_time_ora = time.time()
            # Step 4: Call API for ORA results
            if do_ora:
                while True:
                    print("STEP 4: Call API for ORA results")
                    r = requests.get(
                        f"http://localhost:8203/v1/api/enrichment/complex/{_cluster_to_test_ora}/?cluster_id={_cluster_to_test_ora}",  # noqa
                    )
                    if r.status_code == 200:
                        print("ORA results")
                        _ora_json = r.json()
                        print(_ora_json)
                        break
                    else:
                        print(r.text)
            end_time_ora = time.time()
            print(f"Time to ORA: {end_time_ora - start_time_ora:.4f} seconds")
            # Step 5: Write results
            escribe_csv(
                "measures.csv",
                [
                    ppi_file,
                    f"{(end_cluster_time - start_time):.4f} seconds",  # noqa
                    f"{(end_time_ora - start_time_ora):.4f} seconds",  # noqa
                    f"{(end_time_ora - start_time):.4f} seconds",  # noqa
                ],
            )
    print("Done")


if __name__ == "__main__":
    main(do_ora=False)
