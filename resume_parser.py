import os
import re
import fitz  # PyMuPDF
import docx2txt
import stanza  # type: ignore
from hybrid_model import hybrid_extract_skills

# === Setup NLP pipeline (only once) ===
if not os.path.exists(os.path.expanduser("~") + "/stanza_resources"):
    stanza.download("en", verbose=False)
nlp = stanza.Pipeline("en", processors="tokenize,ner", verbose=False)

# === Regex patterns ===
EMAIL_REGEX = r"[\w\.-]+@[\w\.-]+\.\w+"
PHONE_REGEX = r"(?:(?:\+?91|0)?[-\s]?[6-9]\d{9})"
URL_REGEX = r"https?://(?:www\.)?\S+"


# === Extract text from resume ===
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file format: must be .pdf or .docx")


# === Extract emails, phones, URLs using regex ===
def extract_with_regex(text):
    return {
        "emails": list(set(re.findall(EMAIL_REGEX, text))),
        "phones": list(set(re.findall(PHONE_REGEX, text))),
        "urls": list(set(re.findall(URL_REGEX, text)))
    }


# === Extract name, location, org using Stanza ===
def extract_with_stanza(text):
    doc = nlp(text)
    data = {"name": "", "locations": set(), "organizations": set()}
    for sentence in doc.sentences:
        for ent in sentence.ents:
            if ent.type == "PERSON" and not data["name"]:
                data["name"] = ent.text.strip()
            elif ent.type in ("GPE", "LOC"):
                data["locations"].add(ent.text.strip())
            elif ent.type == "ORG":
                data["organizations"].add(ent.text.strip())
    return {
        "name": data["name"],
        "locations": list(data["locations"]),
        "organizations": list(data["organizations"])
    }


# === Main resume parser function ===
def parse_resume(file_path, target_role=None, job_skill_data=None):
    try:
        text = extract_text(file_path)
        regex_data = extract_with_regex(text)
        stanza_data = extract_with_stanza(text)
        user_skills = hybrid_extract_skills(text)

        result = {
            "name": stanza_data["name"],
            "emails": regex_data["emails"],
            "phones": regex_data["phones"],
            "urls": regex_data["urls"],
            "locations": stanza_data["locations"],
            "organizations": stanza_data["organizations"],
            "skills": user_skills,
            "raw_text_preview": text[:500]
        }

        # Optional: match extracted skills with job role
        if target_role and job_skill_data:
            from skill_matcher import compare_skills
            matched, missing, match_percent = compare_skills(user_skills, target_role, job_skill_data)
            result.update({
                "target_role": target_role,
                "matched_skills": matched,
                "missing_skills": missing,
                "match_percent": match_percent
            })

        return result

    except Exception as e:
        return {"error": f"Failed to parse resume: {str(e)}"}
