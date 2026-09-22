import re

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .tools import explain_job_match, list_applications, search_jobs


class AgentChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = str(request.data.get("message", "")).strip()
        if not message:
            return Response({"detail": "message is required."}, status=400)
        lowered_message = message.lower()
        job_id_match = re.search(r"(?:job\s*#?|id\s*)(\d+)", lowered_message)

        if any(word in lowered_message for word in ("application", "follow-up", "follow up", "tracker")):
            res = list_applications(request.user)
            app_list = res.get("data", {}).get("applications", [])
            return Response({
                "response": f"I checked your workspace tracker: You have {len(app_list)} tracked job application(s).",
                "tool_calls": [{"tool": "list_applications", "params": {}}],
                "tool": "list_applications",
                "data": res
            })

        if job_id_match and any(word in lowered_message for word in ("match", "why", "missing", "score")):
            job_id = int(job_id_match.group(1))
            res = explain_job_match(request.user, job_id)
            explanation = res.get("explanation", f"Match score calculated for Job #{job_id}.")
            return Response({
                "response": explanation,
                "tool_calls": [{"tool": "explain_job_match", "params": {"job_id": job_id}}],
                "tool": "explain_job_match",
                "data": res
            })

        if any(word in lowered_message for word in ("find", "search", "job", "role", "python", "django", "fresher")):
            location = "hyderabad" if "hyderabad" in lowered_message else ""
            query = "django" if "django" in lowered_message else "python" if "python" in lowered_message else ""
            res = search_jobs(request.user, query=query, location=location)
            job_list = res.get("data", {}).get("jobs", [])
            return Response({
                "response": f"Found {len(job_list)} job listings matching '{query or 'all'}' in '{location or 'all locations'}'.",
                "tool_calls": [{"tool": "search_jobs", "params": {"query": query, "location": location}}],
                "tool": "search_jobs",
                "data": res
            })

        return Response({
            "response": "JobPilot AI Agent is ready. Ask me to search jobs (e.g. 'Find Python jobs in Hyderabad'), explain match scores ('Why am I a match for Job #1?'), or list your applications.",
            "tool_calls": [],
            "tool": "help",
            "data": {"message": "Try 'Find Django jobs in Hyderabad', 'Why am I a match for Job 1?', or 'Show my applications'."}
        })


