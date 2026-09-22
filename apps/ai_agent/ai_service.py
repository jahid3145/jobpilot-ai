class DemoAIService:
    """Safe local fallback that only summarizes verified matching results."""

    def explain_match(self, match_result):
        matching = ", ".join(match_result["matching_skills"]) or "no recorded required skills"
        missing = ", ".join(match_result["missing_skills"]) or "no required skills missing"
        return (
            f"The deterministic score is {match_result['overall_match']}%. "
            f"Matching skills: {matching}. Missing skills: {missing}."
        )

