import json
import os
from pathlib import Path
from typing import Tuple


def load_medrb_data() -> Tuple[dict, dict]:
    """Load diagnosis and treatment data from local files.

    Checks for production path (/orwd_data/) first, falls back to local data/ directory.

    Returns:
        Tuple[dict, dict]: (diagnosis_data, treatment_data) dictionaries
    """

    # Check for production path first, then local path
    prod_data_dir = Path("/orwd_data") / "data"
    local_data_dir = Path(__file__).parent / "data"

    if prod_data_dir.exists():
        data_dir = prod_data_dir
    else:
        data_dir = local_data_dir

    diagnosis_path = data_dir / "diagnosis.json"
    treatment_path = data_dir / "treatment.json"

    # Load diagnosis data
    if not diagnosis_path.exists():
        raise FileNotFoundError(f"Diagnosis data not found at {diagnosis_path}")

    with open(diagnosis_path) as f:
        diagnosis_data = json.load(f)

    # Load treatment data
    if not treatment_path.exists():
        raise FileNotFoundError(f"Treatment data not found at {treatment_path}")

    with open(treatment_path) as f:
        treatment_data = json.load(f)

    return diagnosis_data, treatment_data


def create_task_list() -> list[dict]:
    """Create unified task list from both diagnosis and treatment datasets.

    Returns:
        list[dict]: List of task dictionaries with unified schema
    """
    diagnosis_data, treatment_data = load_medrb_data()
    tasks = []

    # Process diagnosis cases
    for case_id, case_data in diagnosis_data.items():
        task = {
            "case_id": case_id,
            "task_type": "diagnosis",
            "raw_case": case_data["raw_case"],
            "case_summary": case_data["generate_case"]["case_summary"],
            "expected_output": case_data["generate_case"]["diagnosis_results"],
            "body_category": case_data.get("body_category", []),
            "disorder_category": case_data.get("disorder_category", []),
            "rare_disease": case_data.get("checked_rare_disease", [])
        }
        tasks.append(task)

    # Process treatment cases
    for case_id, case_data in treatment_data.items():
        task = {
            "case_id": case_id,
            "task_type": "treatment",
            "raw_case": case_data["raw_case"],
            "case_summary": case_data["generate_case"]["case_summary"],
            "expected_output": case_data["generate_case"]["treatment_plan_results"],
            "body_category": case_data.get("body_category", []),
            "disorder_category": case_data.get("disorder_category", []),
            "rare_disease": case_data.get("checked_rare_disease", [])
        }
        tasks.append(task)

    print(f"Loaded {len(tasks)} total tasks ({len(diagnosis_data)} diagnosis + {len(treatment_data)} treatment)")

    return tasks
