import json
import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:1.5b-instruct"


def extract_json(content: str):
    """
    Safely extract JSON from the model response.
    """

    content = content.strip()

    # Remove markdown code fences if returned
    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    # Try complete response first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from extra text
    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = content[
            start:end + 1
        ]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "The AI model did not return valid JSON."
    )


def understand_question(
    question: str,
    datasets: dict
):
    """
    Use the local Qwen model only for intent extraction.

    The AI identifies:
    - operation
    - attendance threshold
    - attendance operator

    Pandas performs all calculations.
    """

    dataset_info = {}

    for name, df in datasets.items():

        dataset_info[name] = {
            "columns": list(df.columns),
            "rows": len(df)
        }

    prompt = f"""
You are an intent extraction system for a
data analytics application.

The user has uploaded these datasets:

{json.dumps(dataset_info, indent=2)}

CURRENT USER QUESTION:

{question}

Your ONLY task is to identify the analytical
operation and parameters.

Do NOT calculate anything.

Return ONLY valid JSON.

Do not use markdown.
Do not explain anything.
Do not answer the question.

============================================================
SUPPORTED OPERATIONS
============================================================

1. total_salary

Meaning:
User wants the total or sum of all employee salaries.

Examples:

"What is the total salary?"

"How much do all employees earn?"

"What is the total annual salary?"

Return:

{{
    "operation": "total_salary"
}}


============================================================

2. average_salary

Meaning:
User wants the overall average or mean salary.

Examples:

"What is the average salary?"

"What is the mean annual salary?"

"What is the average employee salary?"

Return:

{{
    "operation": "average_salary"
}}


============================================================

3. highest_salary

Meaning:
User wants the employee with the highest salary.

Examples:

"Who has the highest salary?"

"Who is the highest paid employee?"

"What is the maximum salary?"

"Which employee earns the most?"

Return:

{{
    "operation": "highest_salary"
}}


============================================================

4. average_salary_by_department

Meaning:
User wants salary grouped by department.

Examples:

"What is the average salary by department?"

"Show department-wise average salary."

"Compare average salary between departments."

"Show average salary per department."

Return:

{{
    "operation": "average_salary_by_department"
}}

IMPORTANT:

If the question says:

"by department"

"department-wise"

"department wise"

"per department"

"between departments"

choose:

average_salary_by_department

Do NOT choose average_salary.


============================================================

5. average_attendance

Meaning:
User wants the overall average attendance.

Examples:

"What is the average attendance?"

"What is the mean attendance?"

"What is the average attendance of all employees?"

Return:

{{
    "operation": "average_attendance"
}}


============================================================

6. employees_by_attendance

Meaning:
User wants to SHOW, LIST, FIND, or GET employees
based on an attendance condition.

The operator MUST be determined from the
CURRENT question.

------------------------------------------------------------
ABOVE
------------------------------------------------------------

Words:

above
greater than
more than
over

Return operator:

"above"

Example:

"Show employees with attendance above 90%"

Return:

{{
    "operation": "employees_by_attendance",
    "operator": "above",
    "attendance_threshold": 90
}}

------------------------------------------------------------
BELOW
------------------------------------------------------------

Words:

below
less than
under

Return operator:

"below"

Example:

"Show employees with attendance below 90%"

Return:

{{
    "operation": "employees_by_attendance",
    "operator": "below",
    "attendance_threshold": 90
}}

------------------------------------------------------------
AT LEAST
------------------------------------------------------------

Words:

at least
greater than or equal to
>=

Return operator:

"at_least"

Example:

"Show employees with attendance at least 90%"

Return:

{{
    "operation": "employees_by_attendance",
    "operator": "at_least",
    "attendance_threshold": 90
}}

------------------------------------------------------------
AT MOST
------------------------------------------------------------

Words:

at most
less than or equal to
<=

Return operator:

"at_most"

Example:

"Show employees with attendance at most 90%"

Return:

{{
    "operation": "employees_by_attendance",
    "operator": "at_most",
    "attendance_threshold": 90
}}

------------------------------------------------------------
EQUAL
------------------------------------------------------------

Words:

equal
equal to
equals
exactly
exact
=

Return operator:

"equal"

Example:

"Show employees with attendance equal to 90%"

Return:

{{
    "operation": "employees_by_attendance",
    "operator": "equal",
    "attendance_threshold": 90
}}

CRITICAL:

"equal" means EXACTLY equal.

Never convert:

equal → above

equal → below

equal → at_least

equal → at_most

Always use the CURRENT question only.

Extract the numeric attendance percentage.

If no attendance percentage is specified,
use 90.


============================================================
7. attendance_trend
============================================================

Meaning:
User wants attendance over time or by month.

Examples:

"Show attendance trend by month"

"Show monthly attendance"

"How does attendance change over the months?"

"How has attendance changed over time?"

Return:

{{
    "operation": "attendance_trend"
}}


============================================================
8. unsupported
============================================================

If the question does not match any supported
operation, return:

{{
    "operation": "unsupported"
}}


============================================================
FINAL RULES
============================================================

1. Do not calculate anything.

2. Do not invent data.

3. Do not answer the user's question.

4. Do not use previous questions.

5. Analyze ONLY the current question.

6. Return exactly ONE JSON object.

7. Do not return markdown.

8. Do not add explanations.

9. For attendance filtering, always extract:
   - operator
   - attendance_threshold

10. "average salary by department" must be:
    average_salary_by_department

11. "average salary" without department must be:
    average_salary

12. "highest salary" or "highest paid employee" must be:
    highest_salary
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0
            }
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    content = result[
        "message"
    ][
        "content"
    ]

    return extract_json(content)