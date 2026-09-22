# JobPilot AI — Technical Interview Guide for Freshers

This guide prepares a candidate to present and defend **JobPilot AI** in technical interviews for Python Developer, Django Developer, and DRF Backend Engineer roles.

---

## 1. Project Pitches

### 30-Second Elevator Pitch
"I built **JobPilot AI**, a backend-first career assistant using **Python, Django REST Framework, and PostgreSQL**. It parses candidate PDF resumes, compares candidate profiles against job listings using a **transparent deterministic multi-factor algorithm**, tracks application lifecycles, and features a **safe, tool-calling AI agent** that helps job seekers discover opportunities and generate tailored cover letters without hallucinating candidate details or automatically submitting applications."

### 1-Minute Pitch
"JobPilot AI addresses a major pain point for job seekers: tracking multiple applications while understanding why they match specific job requirements. 

Using **Django REST Framework and Simple JWT**, I implemented secure authentication and candidate profile management. I built a private PDF resume extraction service using `pypdf` and rule-based parsing. 

For job matching, instead of relying solely on an opaque LLM, I engineered a **deterministic scoring algorithm** weighted across skills (50%), experience (20%), location (10%), salary (10%), and education (10%). 

I also created a **tool-calling AI agent** that routes natural language user requests to validated internal service methods like `search_jobs`, `calculate_job_match`, and `generate_cover_letter`. The system includes Celery task definitions, comprehensive automated unit and API test suites, and clean documentation."

### 3-Minute Comprehensive Walkthrough
"When designing JobPilot AI, my focus was on building a clean, scalable, maintainable Python backend architecture. 

**Core Components & Architecture**:
1. **User & Profile Management**: Extended authentication using Django Simple JWT and custom `CandidateProfile` supporting skills, desired locations, salary expectations, and experience levels.
2. **Resume Parser**: Private PDF file upload handling, text extraction, and rule-based keyword extraction that structures unstructured PDF text into JSON fields (`skills`, `education`, `experience`). Database constraints enforce exactly one primary resume per user.
3. **Job Management & Ingestion**: Designed an extensible `JobSource` interface (`MockJobSource`, `ApiJobSource`, `UserImportedJobSource`) that normalizes job feeds from various channels into a unified `Job` model with deduplication constraints.
4. **Deterministic Match Engine**: Formulated a weighted scoring engine that compares a candidate's profile against job requirements, returning a 0-100% score with precise sub-component breakdowns and missing skill analysis.
5. **AI Integration & Agent Architecture**: Built an `AIService` abstraction with mock fallbacks alongside a controlled tool-calling agent (`JobPilotAgent`). The agent validates user intent and executes allowed internal python tools, enforcing strict permission scoping and preventing unauthorized third-party actions.
6. **Application Tracker & Notifications**: Comprehensive status workflow (`SAVED`, `APPLIED`, `INTERVIEW`, `REJECTED`, `SELECTED`, `WITHDRAWN`), follow-up notification triggers, and cover letter generation constrained strictly to verified user data."

---

## 2. Core Technical Q&A

### Q1: Why did you choose Django & Django REST Framework (DRF)?
**Answer**: Django provides an out-of-the-box battery-included ecosystem with a secure ORM, authentication system, admin interface, and database migration framework. DRF extends Django by offering robust REST API features like serializers for data validation, ViewSets, permission classes, search/filtering backends, and OpenAPI schema generation.

### Q2: Why did you choose MySQL over SQLite for production?
**Answer**: MySQL provides full ACID compliance, high performance for read/write workloads, native JSON data column support (crucial for storing candidate skills and parsed resume JSON data), and robust database constraint enforcement.


### Q3: Why JWT (Simple JWT) authentication?
**Answer**: JWTs are stateless and ideal for RESTful APIs consumed by mobile apps or single-page applications (React/Next.js). Simple JWT handles access token issuance (short-lived) and refresh token rotation, keeping database lookup overhead low per API request.

### Q4: Why Celery and Redis?
**Answer**: Heavy tasks like extracting text from large PDF resumes or processing bulk job ingestion feeds can block Django's HTTP request-response cycle. Offloading these CPU/IO bound tasks to Celery workers with Redis as a message broker ensures fast API response times.

### Q5: How does your AI Agent differ from a simple Chatbot?
**Answer**: A chatbot generates unstructured text responses based on prompt context. An **AI Agent**, on the other hand, possesses **tool-calling capabilities** — it evaluates user intent, selects an appropriate internal Python tool (such as `search_jobs` or `create_application`), validates parameters against strict JSON schemas, executes the business logic under authenticated user permissions, and returns structured data.

### Q6: How does your Job Matching engine work?
**Answer**: The matching engine is strictly deterministic and transparent. Scores are computed across five weighted parameters:
- **Skills Match** (50% weight): Jaccard/set intersection between candidate skills and job required/preferred skills.
- **Experience Match** (20% weight): Compares candidate years of experience against job minimum requirement.
- **Location Match** (10% weight): Checks string overlap or preferred location match.
- **Salary Match** (10% weight): Evaluates overlap between candidate desired salary range and job budget.
- **Education Match** (10% weight): Evaluates education qualification match.

### Q7: How do you prevent duplicate job listings and duplicate applications?
**Answer**: 
- For Jobs: A unique database constraint on `(source, external_job_id)` prevents re-ingesting identical external jobs.
- For Applications: A `UniqueConstraint(fields=['user', 'job'])` on the `Application` model ensures a user cannot submit multiple active applications for the same job.

### Q8: How is security handled in your project?
**Answer**:
1. All API endpoints enforce authentication via `IsAuthenticated` permission classes.
2. Object-level ownership checks prevent users from accessing or modifying other candidates' resumes or applications.
3. Private file storage prevents direct public URL access to uploaded PDF resumes.
4. Secrets and credentials are managed strictly through `.env` environment variables.
5. The AI agent operates on an allowlist of internal tools with read/write safety boundaries (e.g. no auto-submitting job applications).

---

## 3. Resume-Ready Bullet Points

- Developed **JobPilot AI**, a backend-first career management platform built with **Python, Django REST Framework, and MySQL** featuring JWT authentication, OpenAPI docs, and an interactive Web UI dashboard.
- Engineered a **deterministic multi-factor job matching engine** calculating weighted match percentages (skills 50%, experience 20%, location/salary/education 30%) with missing skill gap identification.
- Designed a **controlled tool-calling AI agent** executing internal APIs (`search_jobs`, `calculate_job_match`, `generate_cover_letter`, `create_application`) with strict permission boundaries and fallback provider abstractions.
- Implemented **private PDF resume processing** using text extraction and rule-based keyword parsing to extract structured JSON profile data.
- Built **application lifecycle tracking** with follow-up notifications, fact-constrained cover letter generation, duplicate prevention constraints, and comprehensive unit/API test suites.
