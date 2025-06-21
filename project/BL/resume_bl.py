def form_response(resume):
    return {
        "resume_id": resume[0],
        "user_id": resume[1],
        "job_title": resume[2],
        "education": resume[3],
        "work_xp": resume[4],
        "skills": resume[5],
        "is_active": resume[6]
    }