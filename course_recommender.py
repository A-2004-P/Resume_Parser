def dummy_course_suggestions(missing_skills):
    base_url = "https://www.udemy.com/courses/search/?q="
    return {skill: f"{base_url}{skill.replace(' ', '+')}" for skill in missing_skills}
