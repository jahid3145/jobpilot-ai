# Controlled JobPilot agent

JobPilot uses an agent pattern only for choosing from approved internal operations. It is not an unrestricted autonomous process or a general web browser.

## Available tools

- `search_jobs`: searches the local JobPilot job database.
- `calculate_job_match`: calculates the deterministic score for the signed-in candidate.
- `explain_job_match`: turns the verified score and skill lists into a short explanation.
- `list_applications`: returns only the signed-in candidate's tracker items.

The `/api/agent/chat/` endpoint selects among these based on a small intent parser. The website uses the same tool functions. This is a reliable free/local fallback when no LLM key is available.

## Safety rules

The agent does not submit applications, send emails, modify resumes, delete records, scrape websites, call shell commands, invent salaries, or access arbitrary URLs. All data-changing operations remain normal authenticated application endpoints under user control.

## Example prompts

- `Find Python Django jobs in Hyderabad`
- `Show my applications`
- `Why am I a match for job 3?`

An optional LLM provider can later be added behind the `DemoAIService` interface. It must receive only relevant, verified profile and job facts and should never replace deterministic numerical scoring.
