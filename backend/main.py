import os
import requests
import pandas as pd

from typing import Annotated

from fastapi import (
    FastAPI,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from services.file_service import (
    save_and_read_file
)

from services.ai_service import (
    understand_question
)

from services.analysis_service import (
    total_salary,
    average_salary,
    highest_salary,
    average_attendance,
    employees_by_attendance,
    average_salary_above_attendance,
    average_salary_by_department,
    attendance_trend
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Darwinbox AI Data Q&A",
    description="AI-powered data analysis application",
    version="1.0.0",
    openapi_version="3.0.3"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATASET STORAGE
# ============================================================

datasets = {}


# ============================================================
# LOAD SAVED DATASETS
# ============================================================

def load_saved_datasets():

    loaded_datasets = {}

    upload_dir = "uploads"

    if not os.path.exists(upload_dir):
        return loaded_datasets

    for filename in os.listdir(upload_dir):

        file_path = os.path.join(
            upload_dir,
            filename
        )

        if not os.path.isfile(file_path):
            continue

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in [
            ".csv",
            ".xlsx",
            ".xls"
        ]:
            continue

        try:

            if extension == ".csv":

                df = pd.read_csv(
                    file_path
                )

            else:

                df = pd.read_excel(
                    file_path
                )

            if df.empty:
                continue

            dataset_name = os.path.splitext(
                filename
            )[0]

            loaded_datasets[
                dataset_name
            ] = df

            print(
                f"Loaded dataset: "
                f"{filename} "
                f"({len(df)} rows)"
            )

        except Exception as e:

            print(
                f"Could not load "
                f"{filename}: {e}"
            )

    return loaded_datasets


# ============================================================
# RESTORE DATASETS AT STARTUP
# ============================================================

datasets = load_saved_datasets()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "Darwinbox AI Data Q&A API is running"
    }


# ============================================================
# UPLOAD FILES
# ============================================================

@app.post("/upload")
async def upload_files(
    files: Annotated[
        list[UploadFile],
        File(...)
    ]
):

    global datasets

    uploaded_files = []

    for file in files:

        result = await save_and_read_file(
            file
        )

        df = result["dataframe"]

        dataset_name = os.path.splitext(
            result["filename"]
        )[0]

        datasets[
            dataset_name
        ] = df

        uploaded_files.append(
            {
                "filename":
                    result["filename"],

                "rows":
                    len(df),

                "columns":
                    list(df.columns)
            }
        )

    return {
        "message":
            "Files uploaded successfully",

        "files":
            uploaded_files
    }


# ============================================================
# GET DATASETS
# ============================================================

@app.get("/datasets")
def get_datasets():

    global datasets

    # Reload files if memory was cleared
    if not datasets:

        datasets = load_saved_datasets()

    result = []

    for name, df in datasets.items():

        result.append(
            {
                "name":
                    name,

                "filename":
                    f"{name}.csv",

                "rows":
                    len(df),

                "columns":
                    list(df.columns)
            }
        )

    return {
        "datasets":
            result
    }


# ============================================================
# OLD DIRECT ANALYSIS ENDPOINT
# ============================================================

@app.get(
    "/analysis/average-salary-above-attendance"
)
def analyze_average_salary():

    global datasets

    if not datasets:

        datasets = load_saved_datasets()

    result = average_salary_above_attendance(
        datasets,
        attendance_threshold=90
    )

    return result


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    global datasets

    # --------------------------------------------------------
    # Restore datasets if FastAPI reload cleared memory
    # --------------------------------------------------------

    if not datasets:

        datasets = load_saved_datasets()

    # --------------------------------------------------------
    # Still no datasets
    # --------------------------------------------------------

    if not datasets:

        return {
            "answer":
                "Please upload data files before asking a question."
        }

    try:

        # ====================================================
        # STEP 1
        # Let the local AI understand the question
        # ====================================================

        intent = understand_question(
            request.question,
            datasets
        )

        operation = intent.get(
            "operation"
        )

        # ====================================================
        # STEP 2
        # TOTAL SALARY
        # ====================================================

        if operation == "total_salary":

            result = total_salary(
                datasets
            )

            return {
                "question":
                    request.question,

                "intent":
                    intent,

                "result":
                    result
            }
        # ====================================================
# STEP 3: AVERAGE SALARY
# ====================================================

        if operation == "average_salary":

            result = average_salary(
                datasets
            )

            return {
                "question": request.question,
                "intent": intent,
                "result": result
            }


        # ====================================================
        # STEP 4: HIGHEST SALARY
        # ====================================================

        if operation == "highest_salary":

            result = highest_salary(
                datasets
            )

            return {
                "question": request.question,
                "intent": intent,
                "result": result
            }

        # ====================================================
        # STEP 3
        # AVERAGE SALARY BY DEPARTMENT
        # ====================================================

        if operation == "average_salary_by_department":

            result = average_salary_by_department(
                datasets
            )

            return {
                "question":
                    request.question,

                "intent":
                    intent,

                "result":
                    result
            }

        # ====================================================
        # STEP 4
        # AVERAGE ATTENDANCE
        # ====================================================

        if operation == "average_attendance":

            result = average_attendance(
                datasets
            )

            return {
                "question":
                    request.question,

                "intent":
                    intent,

                "result":
                    result
            }

        # ====================================================
        # STEP 5
        # EMPLOYEES BY ATTENDANCE
        # ====================================================

        if operation == "employees_by_attendance":

            threshold = intent.get(
                "attendance_threshold",
                90
            )

            operator = intent.get(
                "operator",
                "above"
            )

            result = employees_by_attendance(
                datasets,
                attendance_threshold=float(
                    threshold
                ),
                operator=operator
            )

            return {
                "question":
                    request.question,

                "intent":
                    intent,

                "result":
                    result
            }

        # ====================================================
        # STEP 6
        # ATTENDANCE TREND
        # ====================================================

        if operation == "attendance_trend":

            result = attendance_trend(
                datasets
            )

            return {
                "question":
                    request.question,

                "intent":
                    intent,

                "result":
                    result
            }

        # ====================================================
        # UNSUPPORTED QUESTION
        # ====================================================

        return {
            "question":
                request.question,

            "intent":
                intent,

            "answer":
                (
                    "I understood your question, "
                    "but this analysis is not supported yet."
                )
        }

    # ========================================================
    # OLLAMA ERROR
    # ========================================================

    except requests.RequestException:

        return {
            "answer":
                (
                    "The local AI model is not available. "
                    "Please make sure Ollama is running."
                )
        }

    # ========================================================
    # OTHER ERROR
    # ========================================================

    except Exception as e:

        return {
            "answer":
                "Unable to process the question.",

            "error":
                str(e)
        }