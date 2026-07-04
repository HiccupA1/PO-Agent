from typing import Any


class MockLLMService:
    def generate(
        self,
        task: str,
        user_input: str,
        product_context: dict[str, Any],
        backlog_items: list[dict[str, Any]],
    ) -> str:
        if task == "draft_acceptance_criteria":
            return self._draft_acceptance_criteria(user_input, product_context)
        if task == "decompose_epic":
            return self._decompose_epic(user_input, backlog_items)
        if task == "check_dor":
            return self._check_dor(user_input)
        return "Unsupported task."

    def _draft_acceptance_criteria(self, user_input: str, product_context: dict[str, Any]) -> str:
        product_name = product_context.get("product_name", "the product")
        return (
            f"Draft acceptance criteria for {product_name}:\n"
            f"Story/context: {user_input}\n\n"
            "1. Given the user is eligible for the workflow, when they start the action, then the system shows the required next step clearly.\n"
            "2. Given valid information is provided, when the user submits, then the system confirms the request and records the outcome.\n"
            "3. Given required information is missing or invalid, when the user submits, then the system explains what must be corrected.\n"
            "4. Given the workflow is completed, when the Product Owner reviews the item, then the result can be verified through an observable system state."
        )

    def _decompose_epic(self, user_input: str, backlog_items: list[dict[str, Any]]) -> str:
        related = ", ".join(item["id"] for item in backlog_items[:2])
        return (
            f"Epic decomposition draft:\n{user_input}\n\n"
            "Proposed user stories:\n"
            "1. As a Product Owner, I want to capture the primary user goal so that the team can align on business value.\n"
            "2. As a delivery team member, I want the workflow split into testable slices so that each story can be estimated independently.\n"
            "3. As a stakeholder, I want review checkpoints so that important assumptions are validated before sprint planning.\n\n"
            f"Referenced sample backlog items: {related}.\n"
            "Review note: confirm each story has independent value, clear acceptance criteria, and manageable size."
        )

    def _check_dor(self, user_input: str) -> str:
        return (
            f"Definition of Ready check:\n{user_input}\n\n"
            "Ready signals:\n"
            "- User or stakeholder is identifiable.\n"
            "- Desired outcome is stated.\n"
            "- Acceptance criteria can be tested.\n\n"
            "Gaps to review:\n"
            "- Confirm dependencies and edge cases.\n"
            "- Add sizing notes if the team will estimate this soon.\n"
            "- Validate that success metrics or expected business value are explicit.\n\n"
            "Recommendation: human review required before sprint commitment."
        )
