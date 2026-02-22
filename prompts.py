"""Grading prompt templates for MedRBench evaluation."""

DIAGNOSIS_GRADER_TEMPLATE = """You are evaluating a medical diagnosis answer against a reference diagnosis.

# Reference Diagnosis:
{reference_diagnosis}

# Student Answer:
{student_answer}

# Grading Instructions:

Your task is to determine if the student's diagnosis is **semantically equivalent** to the reference diagnosis, even if worded differently.

**Grade as CORRECT if:**
- The core diagnosis matches the reference (e.g., "acute appendicitis" matches "appendicitis")
- Minor wording differences don't change medical meaning
- The diagnosis captures the primary pathology correctly
- Additional correct details are provided that don't contradict the reference

**Grade as INCORRECT if:**
- The primary diagnosis is different or missing
- The diagnosis is anatomically or pathologically incorrect
- Critical diagnostic elements are omitted
- The answer provides a differential diagnosis list instead of a final diagnosis

**Important Notes:**
- Medical terminology may vary (e.g., "MI" vs "myocardial infarction" - both correct)
- Specificity is good but not always required (e.g., "pneumonia" is correct even if reference says "bacterial pneumonia" if context doesn't contradict)
- Focus on clinical correctness, not exact phrasing

Return your answer in the following JSON format:
{{
    "explanation": "Brief explanation of your grading decision",
    "grade": "CORRECT" or "INCORRECT"
}}

Return ONLY the JSON, no other text.""".strip()

TREATMENT_GRADER_TEMPLATE = """You are evaluating a medical treatment plan answer against a reference treatment plan.

# Reference Treatment Plan:
{reference_treatment}

# Student Answer:
{student_answer}

# Grading Instructions:

Your task is to determine if the student's treatment plan is **medically appropriate and semantically equivalent** to the reference treatment plan.

**Grade as CORRECT if:**
- The primary treatment intervention matches the reference
- The treatment approach is clinically appropriate for the condition
- Minor variations in dosing or administration that are within standard of care
- Additional appropriate supportive treatments are included

**Grade as INCORRECT if:**
- The primary treatment modality is different or missing
- The treatment is medically inappropriate or contraindicated
- Critical treatment components are omitted
- The treatment doesn't address the primary pathology

**Important Notes:**
- Treatment plans may have acceptable variations (e.g., different antibiotics in same class)
- Generic vs brand names are equivalent
- Dosing variations within standard range are acceptable
- Supportive care additions don't make it incorrect
- Focus on therapeutic equivalence, not exact matching

Return your answer in the following JSON format:
{{
    "explanation": "Brief explanation of your grading decision",
    "grade": "CORRECT" or "INCORRECT"
}}

Return ONLY the JSON, no other text.""".strip()
