import streamlit as st
from resume_parser import parse_resume
from skill_matcher import load_job_skills, compare_skills
from course_recommender import dummy_course_suggestions
import pandas as pd

st.set_page_config(page_title="Skill Gap Analyzer", layout="wide")

st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["Resume Parser", "Skill Gap Analyzer"])

if page == "Resume Parser":
    st.title("📄 Resume Parser")
    uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1]
        with open(f"temp_resume.{file_ext}", "wb") as f:
            f.write(uploaded_file.read())

        resume_data = parse_resume(f"temp_resume.{file_ext}")
        if "error" in resume_data:
            st.error(resume_data["error"])
        else:
            st.subheader("📊 Resume Extracted Info")
            table_data = {
                "Field": ["Name", "Emails", "Phones", "URLs", "Locations", "Skills"],
                "Values": [
                    resume_data["name"],
                    ", ".join(resume_data["emails"]),
                    ", ".join(resume_data["phones"]),
                    ", ".join(resume_data["urls"]),
                    ", ".join(resume_data["locations"]),
                    ", ".join(resume_data["skills"]),
                ]
            }
            st.table(pd.DataFrame(table_data))

elif page == "Skill Gap Analyzer":
    st.title("🧠 Skill Gap Analyzer")
    uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"], key="analyzer")
    role = st.selectbox("🎯 Select your target role", ["Data Scientist", "Web Developer", "Product Manager"])

    if uploaded_file and role:
        file_ext = uploaded_file.name.split('.')[-1]
        with open(f"temp_resume.{file_ext}", "wb") as f:
            f.write(uploaded_file.read())

        resume_data = parse_resume(f"temp_resume.{file_ext}")
        if "error" in resume_data:
            st.error(resume_data["error"])
        else:
            job_data = load_job_skills()
            matched, missing, match_percent = compare_skills(resume_data['skills'], role, job_data)

            st.subheader("📋 Skill Match Report")
            skill_df = pd.DataFrame({
                "Skill Type": ["Matched"] * len(matched) + ["Missing"] * len(missing),
                "Skill": matched + missing
            })
            st.dataframe(skill_df, use_container_width=True)

            st.markdown(f"**✅ Match Percentage:** `{match_percent}%`")

            st.subheader("🎓 Recommended Courses")
            course_df = dummy_course_suggestions(missing)
            st.dataframe(course_df, use_container_width=True)