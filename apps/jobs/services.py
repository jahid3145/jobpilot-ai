from decimal import Decimal


def normalize_terms(values):
    return {str(value).strip().lower() for value in values if str(value).strip()}


class JobMatchingService:
    weights = {"skills": 50, "experience": 20, "location": 10, "salary": 10, "education": 10}

    def __init__(self, profile, resume=None):
        self.profile = profile
        self.resume = resume

    def candidate_skills(self):
        resume_skills = []
        if self.resume:
            resume_skills = self.resume.parsed_data.get("skills", [])
        return normalize_terms([*self.profile.skills, *resume_skills, *self.profile.preferred_technologies])

    def calculate_skill_match(self, job):
        required_skills = normalize_terms(job.required_skills)
        if not required_skills:
            return 100, [], []
        candidate_skills = self.candidate_skills()
        matching_skills = sorted(required_skills & candidate_skills)
        missing_skills = sorted(required_skills - candidate_skills)
        return round(len(matching_skills) / len(required_skills) * 100), matching_skills, missing_skills

    def calculate_experience_match(self, job):
        experience = Decimal(self.profile.years_of_experience)
        required = Decimal(job.experience_min)
        if required == 0 or experience >= required:
            return 100
        return round(float(experience / required * 100))

    def calculate_location_match(self, job):
        preferred_locations = normalize_terms([self.profile.location, *self.profile.preferred_locations])
        if not job.location or not preferred_locations:
            return 50
        return 100 if job.location.strip().lower() in preferred_locations else 0

    def calculate_salary_match(self, job):
        if not self.profile.minimum_salary or not job.salary_max:
            return 50
        if job.salary_max >= self.profile.minimum_salary:
            return 100
        return round(job.salary_max / self.profile.minimum_salary * 100)

    def calculate_education_match(self, job):
        return 100 if not self.profile.education else 75

    def calculate_match(self, job):
        skill_score, matching_skills, missing_skills = self.calculate_skill_match(job)
        breakdown = {
            "skills": skill_score,
            "experience": self.calculate_experience_match(job),
            "location": self.calculate_location_match(job),
            "salary": self.calculate_salary_match(job),
            "education": self.calculate_education_match(job),
        }
        overall = round(sum(breakdown[name] * weight for name, weight in self.weights.items()) / 100)
        return {
            "overall_match": overall,
            "breakdown": breakdown,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "score_method": "deterministic_v1",
        }


class JobSource:
    """Abstract base class for job sources."""

    def fetch_jobs(self):
        raise NotImplementedError


class MockJobSource(JobSource):
    """Returns mock/demo job datasets for testing and development."""

    def fetch_jobs(self):
        return [
            {
                "title": "Python Developer",
                "company": "Fictional Tech",
                "location": "Hyderabad",
                "description": "Build backend APIs with Python and Django.",
                "required_skills": ["Python", "Django", "SQL"],
                "preferred_skills": ["Docker", "Redis"],
                "salary_min": 400000,
                "salary_max": 700000,
                "source": "mock",
                "external_job_id": "MOCK-1001",
            },
            {
                "title": "Django REST Framework Backend Developer",
                "company": "Fictional Systems",
                "location": "Hyderabad",
                "description": "Develop scalable REST APIs using Django REST Framework.",
                "required_skills": ["Python", "Django", "DRF", "PostgreSQL"],
                "preferred_skills": ["Celery", "Docker"],
                "salary_min": 500000,
                "salary_max": 900000,
                "source": "mock",
                "external_job_id": "MOCK-1002",
            },
        ]


class ApiJobSource(JobSource):
    """Fetches job listings from an external authorized REST API."""

    def __init__(self, api_url=None, api_key=None):
        self.api_url = api_url
        self.api_key = api_key

    def fetch_jobs(self):
        # Graceful placeholder fallback if no external API configured
        return []


class UserImportedJobSource(JobSource):
    """Normalizes job data imported from JSON or user submission."""

    def __init__(self, raw_data):
        self.raw_data = raw_data if isinstance(raw_data, list) else [raw_data]

    def fetch_jobs(self):
        normalized = []
        for item in self.raw_data:
            normalized.append(
                {
                    "title": item.get("title", "Untitled Job"),
                    "company": item.get("company", "Unknown Company"),
                    "location": item.get("location", "Remote"),
                    "description": item.get("description", ""),
                    "required_skills": item.get("required_skills", []),
                    "preferred_skills": item.get("preferred_skills", []),
                    "salary_min": item.get("salary_min"),
                    "salary_max": item.get("salary_max"),
                    "source": item.get("source", "user_import"),
                    "external_job_id": item.get("external_job_id"),
                    "external_url": item.get("external_url", ""),
                }
            )
        return normalized


class JobIngestionService:
    """Ingests job records into PostgreSQL/SQLite while preventing duplicates."""

    @staticmethod
    def create_or_update_job(job_data):
        from apps.jobs.models import Job

        external_id = job_data.get("external_job_id")
        title = job_data.get("title")
        company = job_data.get("company")

        # Duplicate check by external_job_id or (title + company)
        if external_id:
            job, created = Job.objects.update_or_create(
                external_job_id=external_id,
                defaults=job_data,
            )
            return job

        job, created = Job.objects.update_or_create(
            title=title,
            company=company,
            defaults=job_data,
        )
        return job

    @classmethod
    def ingest_from_source(cls, source: JobSource):
        jobs_data = source.fetch_jobs()
        ingested_jobs = []
        for data in jobs_data:
            job = cls.create_or_update_job(data)
            ingested_jobs.append(job)
        return ingested_jobs


