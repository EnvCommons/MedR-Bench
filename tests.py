"""Unit tests for MedRBench environment."""

import pytest
from medrb import MedRBench, TaskSpec


def test_task_loading():
    """Test that tasks load correctly."""
    tasks = MedRBench.list_tasks("test")
    assert len(tasks) == 1453  # 957 diagnosis + 496 treatment

    # Check task types
    diagnosis_count = sum(1 for t in tasks if t["task_type"] == "diagnosis")
    treatment_count = sum(1 for t in tasks if t["task_type"] == "treatment")

    assert diagnosis_count == 957
    assert treatment_count == 496


def test_splits():
    """Test available splits."""
    splits = MedRBench.list_splits()
    assert splits == ["test"]


def test_invalid_split():
    """Test that invalid splits raise ValueError."""
    with pytest.raises(ValueError, match="Unknown split"):
        MedRBench.list_tasks("train")


def test_task_spec_validation():
    """Test TaskSpec validation."""
    sample_task = {
        "case_id": "PMC12345",
        "task_type": "diagnosis",
        "raw_case": "Sample case",
        "case_summary": "Summary",
        "expected_output": "Diagnosis",
        "body_category": ["Brain"],
        "disorder_category": ["Infections"],
        "rare_disease": []
    }

    spec = TaskSpec.model_validate(sample_task)
    assert spec.case_id == "PMC12345"
    assert spec.task_type == "diagnosis"


def test_task_structure():
    """Test that tasks have required fields."""
    tasks = MedRBench.list_tasks("test")

    required_fields = [
        "case_id", "task_type", "raw_case", "case_summary",
        "expected_output", "body_category", "disorder_category", "rare_disease"
    ]

    for task in tasks[:5]:  # Check first 5 tasks
        for field in required_fields:
            assert field in task, f"Task missing required field: {field}"

        assert task["task_type"] in ["diagnosis", "treatment"]


def test_secrets_validation():
    """Test that missing API key raises ValueError."""
    sample_task = {
        "case_id": "PMC12345",
        "task_type": "diagnosis",
        "raw_case": "Sample case",
        "case_summary": "Summary",
        "expected_output": "Diagnosis",
        "body_category": ["Brain"],
        "disorder_category": ["Infections"],
        "rare_disease": []
    }

    with pytest.raises(ValueError, match="OpenAI API key must be provided"):
        MedRBench(task_spec=sample_task, secrets={})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
