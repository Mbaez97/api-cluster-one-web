import csv

import os


def detect_file_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension == ".txt":
        return "txt"
    elif file_extension == ".csv":
        return "csv"
    else:
        return "unknown"


def escribe_csv(archivo, data):
    with open(archivo, "a+", newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(data)


def crea_csv(archivo, data):
    with open(archivo, "w+", newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(data)


def lee_csv(archivo, delimiter=","):
    with open(archivo, "r", newline="") as in_file:
        reader = csv.reader(in_file, delimiter=delimiter)
        return list(reader)[1:]


def lee_txt(archivo):
    with open(archivo, "r") as in_file:
        return in_file.readlines()


def parse_ppi_csv_to_txt(
    file_path: str, file_out_path: str, wieght: bool = False
):  # noqa
    """
    Parses PPI data from a CSV file to a text file.

    Parameters:
        file_path (str): The path to the input CSV file.
        file_out_path (str): The path to the output text file.
        wieght (bool, optional): Flag indicating whether to include weights.
        Defaults to False.
    """
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
