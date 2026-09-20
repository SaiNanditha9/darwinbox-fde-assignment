import pandas as pd


# ============================================================
# COMBINE DATASETS
# ============================================================

def get_combined_employee_data(datasets: dict) -> pd.DataFrame:
    """
    Combine employees, attendance and salaries datasets
    using employee_id.
    """

    required_datasets = [
        "employees",
        "attendance",
        "salaries"
    ]

    for dataset in required_datasets:
        if dataset not in datasets:
            raise ValueError(
                f"Required dataset '{dataset}' is missing."
            )

    employees = datasets["employees"].copy()
    attendance = datasets["attendance"].copy()
    salaries = datasets["salaries"].copy()

    combined = employees.merge(
        attendance,
        on="employee_id",
        how="inner"
    )

    combined = combined.merge(
        salaries,
        on="employee_id",
        how="inner"
    )

    return combined


# ============================================================
# 1. TOTAL SALARY
# ============================================================

def total_salary(datasets: dict):
    """
    Calculate total annual salary of all employees.
    """

    if "salaries" not in datasets:
        raise ValueError(
            "Required dataset 'salaries' is missing."
        )

    salaries = datasets["salaries"].copy()

    total = salaries["annual_salary"].sum()

    return {
        "answer": (
            f"The total annual salary is "
            f"₹{total:,.2f}."
        ),
        "total_salary": float(total)
    }


# ============================================================
# 2. AVERAGE SALARY
# ============================================================

def average_salary(datasets: dict):
    """
    Calculate average annual salary.
    """

    if "salaries" not in datasets:
        raise ValueError(
            "Required dataset 'salaries' is missing."
        )

    salaries = datasets["salaries"].copy()

    average = salaries["annual_salary"].mean()

    return {
        "answer": (
            f"The average annual salary is "
            f"₹{average:,.2f}."
        ),
        "average_salary": float(average)
    }


# ============================================================
# 3. HIGHEST SALARY
# ============================================================

def highest_salary(datasets: dict):
    """
    Find the employee with the highest salary.
    """

    combined = get_combined_employee_data(datasets)

    highest = combined.loc[
        combined["annual_salary"].idxmax()
    ]

    employee = {
        "employee_id": highest["employee_id"],
        "name": highest["name"],
        "department": highest["department"],
        "annual_salary": float(
            highest["annual_salary"]
        )
    }

    return {
        "answer": (
            f"{employee['name']} has the highest annual "
            f"salary of ₹{employee['annual_salary']:,.2f}."
        ),
        "employee": employee
    }


# ============================================================
# 4. AVERAGE ATTENDANCE
# ============================================================

def average_attendance(datasets: dict):
    """
    Calculate average attendance percentage.
    """

    if "attendance" not in datasets:
        raise ValueError(
            "Required dataset 'attendance' is missing."
        )

    attendance = datasets["attendance"].copy()

    average = attendance[
        "attendance_percentage"
    ].mean()

    return {
        "answer": (
            f"The average attendance is "
            f"{average:.2f}%."
        ),
        "average_attendance": float(average)
    }


# ============================================================
# 5. EMPLOYEES BY ATTENDANCE
# ============================================================

def employees_by_attendance(
    datasets: dict,
    attendance_threshold: float = 90,
    operator: str = "above"
):
    """
    Find employees based on attendance condition.

    Supported operators:
        above
        below
        at_least
        at_most
        equal
    """

    combined = get_combined_employee_data(datasets)

    attendance = combined[
        "attendance_percentage"
    ]

    if operator == "above":

        filtered = combined[
            attendance > attendance_threshold
        ]

        condition_text = (
            f"above {attendance_threshold}%"
        )

    elif operator == "below":

        filtered = combined[
            attendance < attendance_threshold
        ]

        condition_text = (
            f"below {attendance_threshold}%"
        )

    elif operator == "at_least":

        filtered = combined[
            attendance >= attendance_threshold
        ]

        condition_text = (
            f"at least {attendance_threshold}%"
        )

    elif operator == "at_most":

        filtered = combined[
            attendance <= attendance_threshold
        ]

        condition_text = (
            f"at most {attendance_threshold}%"
        )

    elif operator == "equal":

        filtered = combined[
            attendance == attendance_threshold
        ]

        condition_text = (
            f"equal to {attendance_threshold}%"
        )

    else:

        raise ValueError(
            f"Unsupported attendance operator: {operator}"
        )

    result_data = filtered[
        [
            "employee_id",
            "name",
            "department",
            "attendance_percentage",
            "annual_salary"
        ]
    ].to_dict(orient="records")

    return {
        "answer": (
            f"Found {len(filtered)} employees "
            f"with attendance {condition_text}."
        ),
        "employees_count": len(filtered),
        "data": result_data
    }


# ============================================================
# 6. AVERAGE SALARY ABOVE ATTENDANCE
# ============================================================

def average_salary_above_attendance(
    datasets: dict,
    attendance_threshold: float = 90
):
    """
    Calculate the average annual salary of employees
    whose attendance is above the given threshold.
    """

    combined = get_combined_employee_data(datasets)

    filtered = combined[
        combined["attendance_percentage"]
        > attendance_threshold
    ]

    if filtered.empty:

        return {
            "answer": (
                f"No employees found with attendance "
                f"above {attendance_threshold}%."
            ),
            "average_salary": 0,
            "employees_count": 0,
            "data": []
        }

    average_salary_value = (
        filtered["annual_salary"].mean()
    )

    result_data = filtered[
        [
            "employee_id",
            "name",
            "department",
            "attendance_percentage",
            "annual_salary"
        ]
    ].to_dict(orient="records")

    return {
        "answer": (
            f"The average annual salary of employees "
            f"with attendance above "
            f"{attendance_threshold}% is "
            f"₹{average_salary_value:,.2f}."
        ),
        "average_salary": float(
            average_salary_value
        ),
        "employees_count": len(filtered),
        "data": result_data
    }


# ============================================================
# 7. AVERAGE SALARY BY DEPARTMENT
# ============================================================

def average_salary_by_department(
    datasets: dict
):
    """
    Calculate average salary grouped by department.
    """

    combined = get_combined_employee_data(datasets)

    grouped = (
        combined
        .groupby("department")["annual_salary"]
        .mean()
        .reset_index()
    )

    grouped = grouped.sort_values(
        "annual_salary",
        ascending=False
    )

    result_data = []

    for _, row in grouped.iterrows():

        result_data.append({
            "department": row["department"],
            "average_salary": float(
                row["annual_salary"]
            )
        })

    return {
        "answer": (
            "Average salary calculated by department."
        ),
        "data": result_data,
        "chart": {
            "type": "bar",
            "title": "Average Salary by Department",
            "x_key": "department",
            "y_key": "average_salary"
        }
    }


# ============================================================
# 8. ATTENDANCE TREND
# ============================================================

def attendance_trend(datasets: dict):
    """
    Calculate average attendance by month.
    """

    if "attendance" not in datasets:
        raise ValueError(
            "Required dataset 'attendance' is missing."
        )

    attendance = datasets["attendance"].copy()

    grouped = (
        attendance
        .groupby("month")["attendance_percentage"]
        .mean()
        .reset_index()
    )

    grouped = grouped.rename(
        columns={
            "attendance_percentage":
                "average_attendance"
        }
    )

    result_data = []

    for _, row in grouped.iterrows():

        result_data.append({
            "month": row["month"],
            "average_attendance": float(
                row["average_attendance"]
            )
        })

    return {
        "answer": (
            "Average attendance trend calculated by month."
        ),
        "data": result_data,
        "chart": {
            "type": "line",
            "title": "Attendance Trend",
            "x_key": "month",
            "y_key": "average_attendance"
        }
    }