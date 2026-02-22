"""MedRBench Environment for medical diagnosis and treatment plan evaluation."""

import json
import re
from typing import List, Literal
import openai
from pydantic import BaseModel

from openreward.environments import Environment, JSONObject, ToolOutput, tool, TextBlock

from prompts import DIAGNOSIS_GRADER_TEMPLATE, TREATMENT_GRADER_TEMPLATE
from utils import create_task_list


class TaskSpec(BaseModel):
    """Task specification for MedRBench tasks."""
    case_id: str
    task_type: Literal["diagnosis", "treatment"]
    raw_case: str
    case_summary: str
    expected_output: str
    body_category: list[str]
    disorder_category: list[str]
    rare_disease: list[str]


class AnswerInput(BaseModel, extra="forbid"):
    """Input model for answer tool."""
    answer: str


class MedRBench(Environment):
    """MedRBench environment for evaluating medical diagnosis and treatment plans.

    This environment presents medical case reports and evaluates agent responses
    for either diagnosis or treatment plan recommendations using binary LLM grading.
    """

    def __init__(self, task_spec: JSONObject, secrets: dict[str, str] = {}) -> None:
        """Initialize MedRBench environment.

        Args:
            task_spec: Task specification dictionary
            secrets: Dictionary containing API keys (must include "openai_api_key")

        Raises:
            ValueError: If openai_api_key is not provided in secrets
        """
        super().__init__(task_spec)
        self.validated = TaskSpec.model_validate(task_spec)

        # CRITICAL: Use secrets parameter for API key (per CLAUDE.md)
        api_key = secrets.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key must be provided via secrets parameter")

        self.client = openai.AsyncClient(api_key=api_key)

    async def _grade_answer(self, student_answer: str) -> tuple[str, str]:
        """Grade student answer using LLM grader.

        Args:
            student_answer: The answer provided by the agent

        Returns:
            tuple[str, str]: (explanation, grade) where grade is "CORRECT" or "INCORRECT"
        """
        # Select template based on task type
        if self.validated.task_type == "diagnosis":
            template = DIAGNOSIS_GRADER_TEMPLATE
            grader_prompt = template.format(
                reference_diagnosis=self.validated.expected_output,
                student_answer=student_answer
            )
        else:  # treatment
            template = TREATMENT_GRADER_TEMPLATE
            grader_prompt = template.format(
                reference_treatment=self.validated.expected_output,
                student_answer=student_answer
            )

        # Retry loop for JSON parsing failures (like HealthBench)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use gpt-5-mini with NO temperature parameter (per CLAUDE.md)
                res = await self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": grader_prompt}]
                )

                grading_response = res.choices[0].message.content or ""

                # Parse JSON response
                grading_dict = self._parse_json(grading_response)

                if "grade" in grading_dict:
                    grade = grading_dict["grade"].upper()
                    if grade in ["CORRECT", "INCORRECT"]:
                        explanation = grading_dict.get("explanation", "")
                        return explanation, grade

                print(f"Invalid grade format (attempt {attempt + 1}/{max_retries}), retrying...")

            except Exception as e:
                print(f"Grading error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    # Default to INCORRECT on persistent failure
                    return "Grading failed after retries", "INCORRECT"

        return "Grading failed", "INCORRECT"

    def _parse_json(self, json_string: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks.

        Args:
            json_string: Raw JSON string from LLM response

        Returns:
            dict: Parsed JSON dictionary
        """
        # Remove markdown code blocks if present
        json_cleaned = re.sub(r"^```json\s*|\s*```$", "", json_string.strip(), flags=re.MULTILINE)
        json_cleaned = re.sub(r"^```\s*|\s*```$", "", json_cleaned.strip(), flags=re.MULTILINE)

        try:
            return json.loads(json_cleaned)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            return {}

    @tool
    async def answer(self, params: AnswerInput) -> ToolOutput:
        """Submit answer for grading.

        Args:
            params: AnswerInput with answer field

        Returns:
            ToolOutput with binary reward (1.0 or 0.0)
        """
        explanation, grade = await self._grade_answer(params.answer)

        reward = 1.0 if grade == "CORRECT" else 0.0

        # Prepare display text
        display_text = f"""# Grading Results

**Task Type:** {self.validated.task_type.title()}
**Grade:** {grade}
**Reward:** {reward:.1f}

**Explanation:**
{explanation}

**Your Answer:**
{params.answer}

**Reference Answer:**
{self.validated.expected_output}
"""

        return ToolOutput(
            metadata={
                "grade": grade,
                "explanation": explanation,
                "task_type": self.validated.task_type,
                "case_id": self.validated.case_id
            },
            blocks=[TextBlock(text=display_text)],
            reward=reward,
            finished=True
        )

    async def get_prompt(self) -> List[TextBlock]:
        """Generate task prompt based on task type.

        Returns:
            List[TextBlock]: Prompt text blocks for the agent
        """
        if self.validated.task_type == "diagnosis":
            prompt = f"""# Medical Diagnosis Task

You are presented with a medical case report. Your task is to provide a diagnosis based on the clinical information provided.

## Case Report:
{self.validated.raw_case}

## Instructions:
- Analyze the clinical presentation, patient history, examination findings, and test results
- Provide your diagnosis
- Use the `answer` tool to submit your diagnosis when ready
- You have one attempt to submit your answer
"""
        else:  # treatment
            prompt = f"""# Medical Treatment Planning Task

You are presented with a medical case report. Your task is to propose an appropriate treatment plan based on the clinical information provided.

## Case Report:
{self.validated.raw_case}

## Instructions:
- Analyze the clinical presentation, patient history, examination findings, and test results
- Propose an appropriate treatment plan
- Use the `answer` tool to submit your treatment plan when ready
- You have one attempt to submit your answer
"""

        return [TextBlock(text=prompt)]

    @classmethod
    def list_tasks(cls, split: str) -> list[JSONObject]:
        """Return list of all tasks for given split.

        Args:
            split: Split name (only "test" is available)

        Returns:
            list[JSONObject]: List of task dictionaries

        Raises:
            ValueError: If split is not "test"
        """
        if split != "test":
            raise ValueError(f"Unknown split: {split}. Only 'test' is available.")

        tasks = create_task_list()
        return tasks

    @classmethod
    def list_splits(cls) -> list[str]:
        """Return available splits.

        Returns:
            list[str]: List of available split names
        """
        return ["test"]
