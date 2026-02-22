# MedRBench Environment

MedRBench is an OpenReward environment for evaluating medical diagnosis and treatment plan generation capabilities of AI agents. The environment presents medical case reports and uses binary LLM grading to assess agent responses.

## Overview

- **Tasks**: 1,453 medical cases (957 diagnosis + 496 treatment)
- **Task Types**: Diagnosis and Treatment Planning
- **Evaluation**: Binary grading (1.0 correct / 0.0 incorrect) using gpt-5-mini
- **Source**: [MedRBench Dataset](https://github.com/MAGIC-AI4Med/MedRBench)

## Installation

```bash
# Clone or navigate to the medrb directory
cd medrb

# Install dependencies
pip install -r requirements.txt
```

## Data

The environment includes local data files:
- **Diagnosis cases**: 957 cases with rare diseases (diagnosis.json, ~14MB)
- **Treatment cases**: 496 cases with rare diseases (treatment.json, ~8.1MB)

Data files are stored in:
- **Local development**: `data/` directory
- **Production deployment**: `/orwd_data/` directory (automatically detected)

## Usage

### Running the Server

```bash
python server.py
```

The server runs on port 8080 by default.

### Testing with an Agent

```bash
export OPENAI_API_KEY="your-api-key"
python test_agent.py
```

### Running Unit Tests

```bash
pytest tests.py -v
```

## Task Structure

Each task contains:
- `case_id`: PubMed Central ID (e.g., "PMC11625232")
- `task_type`: Either "diagnosis" or "treatment"
- `raw_case`: Full medical case report text
- `case_summary`: Structured summary of the case
- `expected_output`: Ground truth answer for grading
- `body_category`: Anatomical categories
- `disorder_category`: Disease categories
- `rare_disease`: Rare disease indicators

## Environment Interface

### Tool

**`answer(params: AnswerInput)`**
- Submit diagnosis or treatment plan for evaluation
- Returns binary reward (1.0 or 0.0)
- Includes grading explanation and reference answer

### Methods

**`get_prompt() -> List[TextBlock]`**
- Returns task-specific prompt (diagnosis or treatment)
- Includes full case report text

**`list_tasks(split: str) -> list[JSONObject]`**
- Returns all 1,453 tasks for "test" split

**`list_splits() -> list[str]`**
- Returns available splits: ["test"]

## Grading

The environment uses gpt-5-mini to grade agent responses with:
- **Semantic equivalence**: Accepts medical terminology variations
- **Binary scoring**: 1.0 (correct) or 0.0 (incorrect)
- **Retry logic**: Up to 3 attempts for robust evaluation

### Grading Criteria

**Diagnosis Tasks:**
- Core diagnosis must match reference
- Medical terminology variations accepted
- Focus on primary pathology

**Treatment Tasks:**
- Primary intervention must match reference
- Clinically appropriate variations accepted
- Therapeutic equivalence over exact matching

## Docker Deployment

```bash
# Build image
docker build -t medrb:latest .

# Run container
docker run -p 8080:8080 -e OPENAI_API_KEY=$OPENAI_API_KEY medrb:latest
```

## File Structure

```
medrb/
├── data/              # Data files
│   ├── diagnosis.json # 957 diagnosis cases (~14MB)
│   └── treatment.json # 496 treatment cases (~8.1MB)
├── medrb.py           # Main environment class
├── server.py          # Server wrapper
├── prompts.py         # Grading templates
├── utils.py           # Data loading utilities
├── test_agent.py      # Agent integration testing
├── tests.py           # Unit tests
├── requirements.txt   # Dependencies
├── Dockerfile         # Container configuration
└── README.md          # This file
```

## Development

### Syntax Check

```bash
python -m py_compile medrb.py prompts.py utils.py server.py
```

### Running Tests

```bash
# Unit tests
pytest tests.py -v

# Integration tests
export OPENAI_API_KEY="your-api-key"
python test_agent.py
```

## Citation

If you use this environment, please cite the MedRBench paper:

```
@article{medrb2024,
  title={MedRBench: A Benchmark for Medical Reasoning},
  author={MAGIC-AI4Med},
  journal={GitHub},
  year={2024},
  url={https://github.com/MAGIC-AI4Med/MedRBench}
}
```

## License

This environment implementation follows the OpenReward framework. The MedRBench dataset is subject to its original license terms.
