import os
import pandas as pd
from fastapi import UploadFile


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_and_read_file(file: UploadFile):

    filename = file.filename

    if not filename:
        raise ValueError("File name is missing.")

    extension = os.path.splitext(filename)[1].lower()

    if extension not in [".csv", ".xlsx", ".xls"]:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            "Only CSV and Excel files are supported."
        )

    file_path = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(contents)

    if extension == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    if df.empty:
        raise ValueError(
            f"{filename} does not contain any data."
        )

    return {
        "filename": filename,
        "path": file_path,
        "dataframe": df
    }