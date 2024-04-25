import random
import os
from libs.lib_manejo_csv import lee_csv


def get_random_color():
    r1 = random.randint(0, 255)
    r2 = random.randint(0, 255)
    r3 = random.randint(0, 255)
    return "#%02X%02X%02X" % (r1, r2, r3)


def get_complex_protein_color():
    return "#%02X%02X%02X" % (255, 0, 0)


def execute_cluster_one(command: str, file_name: str = None):
    print(command)
    os.system(command)
    if file_name:
        response = lee_csv(file_name)
        print(f"mv {file_name} /app/app/media/clusters/{file_name}")
        try:
            os.system(f"mv {file_name} /app/app/media/clusters/{file_name}")
        except Exception as e:
            print(e)
            os.system("mkdir /app/app/media/clusters")
            os.system(f"mv {file_name} /app/app/media/clusters/{file_name}")
        return response
    else:
        response = lee_csv("complex_cluster_response.csv")
        try:
            os.system(
                "mv complex_cluster_response.csv /app/app/media/clusters/complex_cluster_response.csv"
            )
        except Exception as e:
            print(e)
            os.system("mkdir /app/app/media/clusters")
            os.system(
                "mv complex_cluster_response.csv /app/app/media/clusters/complex_cluster_response.csv"
            )
    return response
