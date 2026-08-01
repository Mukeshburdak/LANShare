import zipfile
import os


def compress_file(filepath):
    zip_name = filepath + ".zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(filepath, os.path.basename(filepath))

    return zip_name


def extract_zip(zip_file, destination):
    with zipfile.ZipFile(zip_file, "r") as zipf:
        zipf.extractall(destination)