# MedRBench

[![⭐ OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/Pengcheng/medrb) [![Hugging Face Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-orange)](https://huggingface.co/datasets/MAGIC-AI4Med/MedRBench)

## Description

MedRBench is an environment for evaluating medical diagnosis and treatment plan generation from clinical case reports. Based on the MedRBench benchmark from MAGIC-AI4Med (Shanghai Jiao Tong University / Shanghai AI Lab), it presents rare and complex medical cases and evaluates agent responses using binary LLM grading for semantic equivalence.

## Capabilities

- Medical diagnosis from clinical case reports
- Treatment plan generation for complex medical cases
- Reasoning about rare diseases, body systems, and disorder categories

## Compute Requirements

This benchmark does not require a sandbox.

## License

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Tasks

There is one split in this environment:

- **Test**: 1,453 medical cases
  - Diagnosis: 957 cases
  - Treatment: 496 cases

Each task presents a full medical case report. For diagnosis tasks, the agent must provide a diagnosis. For treatment tasks, the agent must propose a treatment plan.

## Reward Structure

This is a single-turn environment with binary reward:

- **1.0** — Correct (semantically equivalent to the reference)
- **0.0** — Incorrect

Grading is performed by gpt-5-mini using task-specific templates:
- **Diagnosis grading**: Evaluates whether the core diagnosis matches, accepting medical terminology variations (e.g., "MI" vs "myocardial infarction")
- **Treatment grading**: Evaluates therapeutic equivalence, accepting clinically appropriate variations in dosing, drug class, and supportive care

Includes a retry loop (3 attempts) for robust evaluation.

## Data

Data consists of two JSON files stored on the OpenReward platform:
- `diagnosis.json`: 957 diagnosis cases with rare diseases
- `treatment.json`: 496 treatment cases with rare diseases

Source: [MAGIC-AI4Med/MedRBench](https://github.com/MAGIC-AI4Med/MedRBench)

## Tools

| Tool | Description |
|------|-------------|
| `answer` | Submit your diagnosis or treatment plan for binary grading. Returns grade, explanation, and reference answer. |

## Time Horizon

MedRBench is a single-turn environment. The agent receives a medical case report and submits one answer, i.e. a single tool call.

## Environment Difficulty

The original paper evaluates LLMs on diagnosis and treatment tasks:

| Model | Diagnosis | Treatment |
|-------|-----------|-----------|
| DeepSeek-R1 | 89.8% | 30.5% |
| Gemini-2.0-FT | 86.8% | - |
| Qwen-QwQ | 85.1% | - |
| OpenAI-o3-mini | 83.9% | 27.0% |
| Baichuan-M1 | 84.4% | 30.7% |

LLMs achieve >80% on diagnosis with complete information, but treatment planning remains challenging (<31% accuracy).

## Other Environment Requirements

- **OpenAI API key**: Required for LLM-based semantic grading. Pass via `secrets={"openai_api_key": "..."}`.

## Safety

MedRBench evaluates medical reasoning on published case reports and should not be used as a substitute for professional medical advice. The environment does not involve real patient care or clinical decision-making.

## Citations

```bibtex
@article{qiu2025medrbench,
  author    = {Pengcheng Qiu and Chaoyi Wu and Shuyu Liu and Weike Zhao and Ya Zhang and Yanfeng Wang and Weidi Xie},
  title     = {Quantifying the Reasoning Abilities of LLMs on Real-world Clinical Cases},
  journal   = {arXiv preprint arXiv:2503.04691},
  year      = {2025},
  url       = {https://arxiv.org/abs/2503.04691}
}
```
