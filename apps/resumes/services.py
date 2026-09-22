import re


KNOWN_SKILLS = {
    "python", "django", "django rest framework", "drf", "flask", "fastapi", "sql", "mysql",
    "postgresql", "docker", "git", "github", "aws", "azure", "kubernetes", "redis", "celery",
    "javascript", "react", "html", "css", "linux", "rest api", "sqlite",
}


class ResumeParser:
    def extract_pdf_text(self, file_object):
        from pypdf import PdfReader

        reader = PdfReader(file_object)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    def parse(self, text):
        normalized_text = text.lower()
        skills = sorted(skill for skill in KNOWN_SKILLS if skill in normalized_text)
        headings = ("education", "experience", "projects", "certifications")
        sections = {heading: [] for heading in headings}
        active_section = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lowered_line = line.lower().rstrip(":")
            if lowered_line in headings:
                active_section = lowered_line
                continue
            if active_section and len(sections[active_section]) < 10:
                sections[active_section].append(line)
        job_titles = re.findall(r"(?:python|django|backend|software)\s+(?:developer|engineer)", normalized_text)
        return {"skills": skills, "job_titles": sorted(set(job_titles)), **sections}


class ResumeParserService:
    @staticmethod
    def parse_text(text):
        return ResumeParser().parse(text)


