from celery import shared_task

from .models import Resume
from .services import ResumeParser


@shared_task
def parse_resume(resume_id):
    resume = Resume.objects.get(pk=resume_id)
    if not resume.file:
        return {"status": "skipped", "reason": "No file attached."}
    parser = ResumeParser()
    resume.file.open("rb")
    try:
        extracted_text = parser.extract_pdf_text(resume.file)
    finally:
        resume.file.close()
    resume.extracted_text = extracted_text
    resume.parsed_data = parser.parse(extracted_text)
    resume.save(update_fields=("extracted_text", "parsed_data", "updated_at"))
    return {"status": "complete", "resume_id": resume.id}
