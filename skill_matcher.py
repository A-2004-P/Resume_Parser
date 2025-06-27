# 📄 skill_matcher.py

import json
import os


def load_job_skills():
    # Dynamically resolve path relative to this file
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "sample_data", "sample_data", "job_roles_skills.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} not found.")
        
    with open(json_path, "r") as f:
        return json.load(f)


def compare_skills(user_skills, target_role, job_skill_data):
    required_skills = job_skill_data.get(target_role.lower(), [])
    matched = list(set(user_skills) & set(required_skills))
    missing = list(set(required_skills) - set(user_skills))
    match_percent = round(len(matched) / len(required_skills) * 100, 2) if required_skills else 0
    return matched, missing, match_percent
