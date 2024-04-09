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
