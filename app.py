import streamlit as st
from streamlit_calendar import calendar # type: ignore
import pandas as pd
import datetime
from dateparser import parse as parse_date  # type: ignore

from resume_parser import parse_resume
from skill_matcher import load_job_skills, compare_skills
from course_recommender import dummy_course_suggestions
from summarizer import summarize_offer
from digest import add_reminder, send_digest
from gcalendar import schedule_event

# ✅ This must be FIRST Streamlit command
st.set_page_config(page_title="Skill Gap Analyzer", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", [
    "Resume Parser",
    "Skill Gap Analyzer",
    "Smart Assistant",
    "Job Offer Chatbot"
])

# --- 1. Resume Parser ---
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
                "Field": [
                    "Name", "Emails", "Phones", "URLs",
                    "Locations", "Skills", "Qualifications", "Years of Experience"
                ],
                "Values": [
                    resume_data["name"],
                    ", ".join(resume_data["emails"]),
                    ", ".join(resume_data["phones"]),
                    ", ".join(resume_data["urls"]),
                    ", ".join(resume_data["locations"]),
                    ", ".join(resume_data["skills"]),
                    ", ".join(resume_data["qualifications"]),
                    resume_data["years_of_experience"]
                ]
            }
            st.table(pd.DataFrame(table_data))

# --- 2. Skill Gap Analyzer ---
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

            st.subheader("🧮 Resume Info Summary")
            st.markdown(f"- **Name:** {resume_data['name']}")
            st.markdown(f"- **Emails:** {', '.join(resume_data['emails'])}")
            st.markdown(f"- **Phones:** {', '.join(resume_data['phones'])}")
            st.markdown(f"- **Qualifications:** {', '.join(resume_data['qualifications'])}")
            st.markdown(f"- **Years of Experience:** `{resume_data['years_of_experience']}`")

# --- 3. Smart Assistant ---
elif page == "Smart Assistant":
    st.title("🤖 Smart Assistant for Offers")

    st.subheader("📨 Offer Summarizer")
    offer_text = st.text_area("Paste internship/job offer text here:")
    profile_keywords = st.text_input("Enter key skills (comma-separated):", value="Python, Excel, SQL").split(",")

    if st.button("Summarize Offer"):
        summary = summarize_offer(offer_text, profile_keywords)
        st.json(summary)

    st.subheader("🔖 Set a Reminder")
    reminder_text = st.text_input("What should I remind you about?")
    remind_time = st.time_input("Time", datetime.time(17, 0))
    remind_date = st.date_input("Date")
    if st.button("Set Reminder"):
        remind_at = datetime.datetime.combine(remind_date, remind_time).strftime("%Y-%m-%d %H:%M")
        add_reminder("user_001", reminder_text, remind_at)
        st.success("Reminder Set!")

    st.subheader("🔕 View Smart Digest")
    if st.button("Generate Digest Now"):
        send_digest()
        st.info("Digest generated. (Check logs or backend display for demo version)")

    st.subheader("📅 Schedule in Google Calendar")
    g_summary = st.text_input("Event Title")
    g_desc = st.text_area("Event Description")
    start_dt = st.datetime_input("Start Date & Time", value=datetime.datetime.now() + datetime.timedelta(hours=1))
    end_dt = st.datetime_input("End Date & Time", value=start_dt + datetime.timedelta(hours=1))

    if st.button("Add to Calendar"):
        gcal_event = {
            "summary": g_summary,
            "description": g_desc,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat()
        }
        result = schedule_event(gcal_event)
        st.success("Event added to your Google Calendar!")

# --- 4. Job Offer Chatbot ---
elif page == "Job Offer Chatbot":
    st.title("💬 Smart Chatbot Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "offers_data" not in st.session_state:
        st.session_state.offers_data = [
            {"id": 1, "title": "Data Analyst Intern", "company": "Google", "status": "Interested", "description": "Work on SQL dashboards.", "deadline": "2025-07-05 17:00"},
            {"id": 2, "title": "Backend Developer", "company": "Amazon", "status": "Ignore", "description": "Microservices APIs.", "deadline": "2025-07-07 12:00"},
            {"id": 3, "title": "ML Intern", "company": "OpenAI", "status": "Interested", "description": "NLP + transformers", "deadline": "2025-07-04 10:00"}
        ]

    st.subheader("📬 Incoming Job Offers")
    offers_df = pd.DataFrame(st.session_state.offers_data)
    st.dataframe(offers_df, use_container_width=True)

    st.subheader("📅 Daily Job Offer Summary")
    summary_date = st.date_input("Select date to summarize offers")
    if st.button("Summarize Offers for the Day"):
        filtered = [offer for offer in st.session_state.offers_data if offer['deadline'].startswith(str(summary_date))]
        if filtered:
            for offer in filtered:
                st.markdown(f"**{offer['title']}** at **{offer['company']}** - Deadline: `{offer['deadline']}`")
        else:
            st.info("No job offers with deadlines on this date.")

    st.subheader("💬 Chat with Assistant")

# Dropdown Suggestions
suggestions = [
    "Summarize all job offers",
    "What are my interested jobs?",
    "Show job offers for 4th July",
    "Mark calendar for Google tomorrow 5pm",
    "Set deadline for Amazon backend developer Saturday 2pm"
]
selected_suggestion = st.selectbox("💡 Pick a suggestion (optional)", [""] + suggestions)
manual_input = st.text_input("Type your prompt below or select above", value=selected_suggestion if selected_suggestion else "")

# --- Chatbot Logic Function ---
import re

def chatbot_reply(message):
    message_lower = message.lower()
    offers = st.session_state.offers_data

    mark_keywords = ["mark", "add", "schedule", "calendar", "set reminder", "remind", "put", "block"]
    deadline_keywords = ["deadline", "due", "last date", "submission", "close"]
    summarize_keywords = ["summarize", "summary", "overview", "list", "all offers"]
    show_keywords = ["show", "what", "list", "display"]

    found_mark = any(kw in message_lower for kw in mark_keywords)
    found_deadline = any(kw in message_lower for kw in deadline_keywords)
    found_summarize = any(kw in message_lower for kw in summarize_keywords)
    found_show = any(kw in message_lower for kw in show_keywords)

    matched_offer = None
    for offer in offers:
        if offer["company"].lower() in message_lower or offer["title"].lower() in message_lower:
            matched_offer = offer
            break

    # --- Extract potential date using regex ---
    date_match = re.search(r'\d{1,2}(st|nd|rd|th)?\s+july|\s+july\s+\d{1,2}', message_lower)
    date_text = date_match.group() if date_match else message_lower

    dt = parse_date(date_text)

    # --- Mark Calendar ---
    if found_mark and matched_offer and dt:
        end = dt + datetime.timedelta(hours=1)
        schedule_event({
            "summary": f"{matched_offer['title']} @ {matched_offer['company']}",
            "description": matched_offer["description"],
            "start": dt.isoformat(),
            "end": end.isoformat()
        })
        return f"✅ Scheduled `{matched_offer['title']}` at `{matched_offer['company']}` for {dt.strftime('%Y-%m-%d %H:%M')}."

    # --- Show Offers for Specific Date ---
    if found_show and dt:
        dt_str = dt.strftime("%Y-%m-%d")
        filtered = [offer for offer in offers if offer['deadline'].startswith(dt_str)]
        if filtered:
            response = f"📋 Job offers with deadlines on `{dt_str}`:\n"
            for offer in filtered:
                response += f"- {offer['title']} at {offer['company']} (Deadline: {offer['deadline']})\n"
            return response
        else:
            return f"ℹ️ No job offers found with deadlines on `{dt_str}`."

    # --- Show Deadline ---
    if found_deadline and matched_offer:
        return f"🕒 The deadline for `{matched_offer['title']}` at `{matched_offer['company']}` is `{matched_offer['deadline']}`."

    # --- Summarize All Offers ---
    if found_summarize:
        response = "Here are all your job offers:\n"
        for offer in offers:
            response += f"- {offer['title']} at {offer['company']} (Deadline: {offer['deadline']})\n"
        return response

    # --- Show Interested Offers ---
    if "interested" in message_lower and "job" in message_lower:
        response = "Here are your interested job offers:\n"
        for offer in offers:
            if offer["status"].lower() == "interested":
                response += f"- {offer['title']} at {offer['company']} (Deadline: {offer['deadline']})\n"
        return response

    return "🧑‍💻 I'm still learning! You can ask me to summarize offers, show deadlines, mark events, or list jobs for a date."


# --- Chatbot Input & Send ---
if manual_input and st.button("Send"):
    st.session_state.chat_history.append(("You", manual_input))
    bot_reply = chatbot_reply(manual_input)
    st.session_state.chat_history.append(("Bot", bot_reply))

# --- Chat History ---
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)

