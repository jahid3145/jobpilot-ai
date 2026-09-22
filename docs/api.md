# API guide

Interactive OpenAPI documentation is available at `/api/docs/` while the server is running.

## Authentication

- `POST /api/auth/register/` creates an account and empty candidate profile.
- `POST /api/auth/login/` returns JWT access and refresh tokens.
- `POST /api/auth/refresh/` refreshes an access token.
- `POST /api/auth/logout/` blacklists a refresh token.
- `GET /api/auth/me/` returns the authenticated account.

Send JWTs with `Authorization: Bearer <access-token>`. The website uses secure Django sessions after its normal login form.

## Candidate and resumes

- `GET` or `PATCH /api/profile/` reads or updates the caller's candidate profile.
- `GET`, `POST /api/resumes/` lists and uploads the caller's private PDF resumes.
- `POST /api/resumes/{id}/set_primary/` marks a resume as the caller's primary resume.

## Jobs and matching

- `GET /api/jobs/?search=django&location=Hyderabad&min_salary=300000&experience=0&skill=Python` searches active jobs.
- `POST /api/jobs/` creates a manual job for the authenticated caller.
- `GET /api/jobs/{id}/match/` returns a deterministic score and missing skills for the caller.

The job API supports `search`, exact `location` and `employment_type`, salary and experience query parameters, plus ordering such as `?ordering=-salary_max`.

## Applications, assistant, and dashboard

- `GET`, `POST /api/applications/` lists or creates the caller's tracker records.
- `GET`, `PATCH`, `DELETE /api/applications/{id}/` manages one caller-owned application.
- `POST /api/cover-letters/generate/` with `{"job_id": 1}` creates a safe local draft.
- `POST /api/agent/chat/` with `{"message": "Find Django jobs in Hyderabad"}` uses an approved tool.
- `GET /api/dashboard/` returns aggregate statistics and best matches.
- `GET /api/notifications/follow-ups/` returns due follow-ups.

Errors use normal DRF HTTP statuses and validation bodies. Protected endpoints never return another user's profile, resumes, applications, or cover letters.
