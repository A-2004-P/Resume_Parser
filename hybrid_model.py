# hybrid_model.py

import re
import joblib
import os

# Load and clean skill list
def load_skill_list(path="skill_gap_analyzer/job_skills_list.txt"):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    skills = [s.strip().lower() for s in re.split(r'[\n,]+', raw) if s.strip()]
    return [s for s in skills if len(s) > 2 or s in ["r", "c", "c++"]]  # Allow only valid short skills

# Filter out junk predictions like single letters, brackets, etc.
def clean_skills(skills):
    cleaned = []
    for skill in skills:
        skill = skill.strip().lower()
        if len(skill) > 2 and skill.isalpha():
            cleaned.append(skill)
        elif skill in ["r", "c", "c++", "html", "sql"]:
            cleaned.append(skill)
    return list(set(cleaned))

# Rule-based skill extractor
def extract_skills_rule_based(text, skill_list):
    found = []
    lowered_text = text.lower()
    for skill in skill_list:
        if skill in lowered_text:
            found.append(skill)
    return clean_skills(found)

# ML-based prediction
def extract_skills_model(text,
                         model_path="skill_gap_analyzer/models/skill_predictor_pipeline.pkl",
                         binarizer_path="skill_gap_analyzer/models/skill_label_binarizer.pkl"):
    try:
        model = joblib.load(model_path)
        mlb = joblib.load(binarizer_path)
        cleaned_text = re.sub(r'\W+', ' ', text.lower())
        prediction = model.predict([cleaned_text])
        predicted_skills = list(mlb.inverse_transform(prediction)[0])
        return clean_skills(predicted_skills)
    except Exception as e:
        print(f"[Model Skill Extraction Failed]: {e}")
        return []

# Hybrid skill extractor
def hybrid_extract_skills(text):
    skill_list = load_skill_list()
    rule_skills = extract_skills_rule_based(text, skill_list)
    model_skills = extract_skills_model(text)
    return list(set(rule_skills + model_skills))
