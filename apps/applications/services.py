class CoverLetterService:
    def generate(self, profile, resume, job):
        name = profile.full_name or profile.user.get_full_name() or profile.user.username
        skills = profile.skills.copy()
        if resume:
            skills.extend(resume.parsed_data.get("skills", []))
        verified_skills = ", ".join(sorted({str(skill) for skill in skills})[:6]) or "relevant backend development skills"
        headline = profile.professional_headline or "an aspiring backend developer"
        return (
            f"Dear Hiring Team at {job.company},\n\n"
            f"I am writing to express my interest in the {job.title} position. I am {name}, {headline}. "
            f"My verified skills include {verified_skills}.\n\n"
            f"I am particularly interested in this opportunity because it aligns with the role requirements described in the job posting. "
            f"I would welcome the chance to discuss how I can contribute to {job.company}.\n\n"
            f"Sincerely,\n{name}"
        )

