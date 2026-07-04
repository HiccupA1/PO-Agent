import re
from typing import Any

from app.schemas.agent import (
    AcceptanceCriteriaItem,
    AcceptanceCriteriaOutput,
    DefinitionOfReadyResult,
)


class MockLLMService:
    def generate(
        self,
        task: str,
        user_input: str,
        product_context: dict[str, Any],
        backlog_items: list[dict[str, Any]],
    ) -> str | AcceptanceCriteriaOutput:
        if task == "draft_acceptance_criteria":
            return self._draft_acceptance_criteria(user_input, product_context, backlog_items)
        if task == "decompose_epic":
            return self._decompose_epic(user_input, backlog_items)
        if task == "check_dor":
            return self._check_dor(user_input)
        return "Unsupported task."

    def _draft_acceptance_criteria(
        self,
        user_input: str,
        product_context: dict[str, Any],
        backlog_items: list[dict[str, Any]],
    ) -> AcceptanceCriteriaOutput:
        story = self._parse_or_rewrite_story(user_input)
        acceptance_criteria = self._build_acceptance_criteria(story, user_input)
        edge_cases = self._build_edge_cases(user_input)
        non_functional_requirements = self._build_non_functional_requirements(user_input)
        assumptions = self._build_assumptions(story)
        clarification_questions = self._build_clarification_questions(story, user_input, product_context)
        dor = self._score_definition_of_ready(
            story=story,
            user_input=user_input,
            context=product_context,
            acceptance_criteria=acceptance_criteria,
            edge_cases=edge_cases,
            backlog_items=backlog_items,
        )
        human_review_required = dor.score < 100 or bool(clarification_questions)
        review_reason = (
            "Human review is required to confirm missing details, edge cases, and business value before sprint commitment."
            if human_review_required
            else "No major readiness gaps detected by the mock rules; Product Owner review is still recommended before delivery."
        )

        return AcceptanceCriteriaOutput(
            rewritten_user_story=story["rewritten"],
            acceptance_criteria=acceptance_criteria,
            edge_cases=edge_cases,
            non_functional_requirements=non_functional_requirements,
            assumptions=assumptions,
            clarification_questions=clarification_questions,
            definition_of_ready=dor,
            human_review_required=human_review_required,
            review_reason=review_reason,
        )

    def _parse_or_rewrite_story(self, user_input: str) -> dict[str, str | bool]:
        text = " ".join(user_input.strip().split())
        story_match = re.search(
            r"as a[n]?\s+(?P<role>.+?),?\s+i want\s+(?P<goal>.+?)\s+so that\s+(?P<benefit>.+)",
            text,
            flags=re.IGNORECASE,
        )

        if story_match:
            role = self._clean_phrase(story_match.group("role"))
            goal = self._clean_phrase(story_match.group("goal"))
            benefit = self._clean_phrase(story_match.group("benefit"))
            rewritten = f"As a {role}, I want {self._want_phrase(goal)}, so that {benefit}."
            return {
                "already_story": True,
                "explicit_role": True,
                "explicit_benefit": True,
                "role": role,
                "goal": goal,
                "benefit": benefit,
                "rewritten": rewritten,
            }

        lower = text.lower()
        role = self._infer_role(lower)
        goal = self._infer_goal(text)
        benefit = self._infer_benefit(lower)
        rewritten = f"As a {role}, I want {self._want_phrase(goal)}, so that {benefit}."
        return {
            "already_story": False,
            "explicit_role": role != "product user",
            "explicit_benefit": "so that" in lower or " in order to " in lower,
            "role": role,
            "goal": goal,
            "benefit": benefit,
            "rewritten": rewritten,
        }

    def _clean_phrase(self, value: str) -> str:
        return value.strip().rstrip(".").strip()

    def _want_phrase(self, goal: str) -> str:
        if goal.lower().startswith("to "):
            return goal
        return f"to {goal}"

    def _action_phrase(self, goal: str) -> str:
        if goal.lower().startswith("to "):
            return goal
        return f"to {goal}"

    def _infer_role(self, lower_text: str) -> str:
        if "finance" in lower_text or "invoice" in lower_text:
            return "finance approver"
        if "customer" in lower_text or "password" in lower_text:
            return "customer"
        if "purchase order" in lower_text or "users" in lower_text:
            return "user"
        return "product user"

    def _infer_goal(self, text: str) -> str:
        cleaned = self._clean_phrase(text)
        replacements = {
            "Build ": "",
            "build ": "",
            "Create ": "",
            "create ": "",
            "Users should ": "",
            "users should ": "",
        }
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new, 1)
        cleaned = cleaned[:1].lower() + cleaned[1:]
        if "approval flow" in cleaned:
            return f"use an {cleaned}"
        return cleaned

    def _infer_benefit(self, lower_text: str) -> str:
        if "invoice" in lower_text or "approval" in lower_text:
            return "invoice approvals are controlled, visible, and completed on time"
        if "purchase order" in lower_text or "delayed" in lower_text or "notification" in lower_text:
            return "I can respond to delivery risk before it affects the business"
        if "password" in lower_text:
            return "I can regain secure access without contacting support"
        return "the team can deliver the right outcome with less ambiguity"

    def _build_acceptance_criteria(
        self,
        story: dict[str, str | bool],
        user_input: str,
    ) -> list[AcceptanceCriteriaItem]:
        role = str(story["role"])
        goal = str(story["goal"])
        lower = user_input.lower()
        criteria = [
            AcceptanceCriteriaItem(
                id="AC-1",
                title="Start the workflow",
                given=f"a {role} has the required access and context",
                when=f"they start {self._action_phrase(goal)}",
                then="the system presents the required fields, actions, and next step clearly",
            ),
            AcceptanceCriteriaItem(
                id="AC-2",
                title="Complete valid request",
                given="all required information is valid",
                when="the user submits the request",
                then="the system completes the workflow and confirms the outcome",
            ),
            AcceptanceCriteriaItem(
                id="AC-3",
                title="Handle missing or invalid information",
                given="required information is missing, invalid, or incomplete",
                when="the user attempts to continue",
                then="the system prevents completion and explains what must be corrected",
            ),
            AcceptanceCriteriaItem(
                id="AC-4",
                title="Provide status visibility",
                given="the workflow has been started or completed",
                when="an authorized user reviews the item",
                then="the system shows the current status, owner, and latest meaningful update",
            ),
        ]

        if "approval" in lower or "invoice" in lower:
            criteria.append(
                AcceptanceCriteriaItem(
                    id="AC-5",
                    title="Route approval decision",
                    given="an invoice requires review",
                    when="the approver approves, rejects, or requests changes",
                    then="the system records the decision and routes the invoice to the correct next state",
                )
            )
        elif "notification" in lower or "delayed" in lower:
            criteria.append(
                AcceptanceCriteriaItem(
                    id="AC-5",
                    title="Send timely notification",
                    given="a purchase order delay is detected",
                    when="the delay meets the notification rule",
                    then="the system notifies affected users with the purchase order, delay reason, and expected next action",
                )
            )

        return criteria

    def _build_edge_cases(self, user_input: str) -> list[str]:
        lower = user_input.lower()
        edge_cases = [
            "Required fields are missing or contain unsupported values.",
            "The same request is submitted more than once.",
            "The user loses permission or session access during the workflow.",
        ]
        if "invoice" in lower or "approval" in lower:
            edge_cases.extend(
                [
                    "The configured approver is unavailable or inactive.",
                    "The invoice amount exceeds the approval threshold and requires escalation.",
                ]
            )
        elif "notification" in lower or "purchase order" in lower or "delayed" in lower:
            edge_cases.extend(
                [
                    "A delay is resolved before the notification is sent.",
                    "Multiple delays occur for the same purchase order.",
                ]
            )
        elif "password" in lower:
            edge_cases.extend(
                [
                    "The reset token has expired or was already used.",
                    "The account is locked or requires additional verification.",
                ]
            )
        else:
            edge_cases.append("External dependencies are unavailable when the workflow runs.")
        return edge_cases[:5]

    def _build_non_functional_requirements(self, user_input: str) -> list[str]:
        lower = user_input.lower()
        requirements = [
            "The workflow should provide clear feedback within two seconds for normal user actions.",
            "All important state changes should be auditable with timestamp, actor, and outcome.",
            "Validation and error messages should be understandable to non-technical business users.",
        ]
        if "password" in lower:
            requirements.append("Security-sensitive actions should use short-lived tokens and avoid exposing account details.")
        elif "invoice" in lower or "approval" in lower:
            requirements.append("Approval decisions should preserve financial auditability and access control boundaries.")
        return requirements[:4]

    def _build_assumptions(self, story: dict[str, str | bool]) -> list[str]:
        assumptions: list[str] = []
        if not story["already_story"]:
            assumptions.append("The raw feature description was rewritten into a user story format.")
        if not story["explicit_benefit"]:
            assumptions.append("The business value was inferred from the feature description.")
        if story["role"] == "product user":
            assumptions.append("The target user role is not explicit and should be confirmed.")
        assumptions.append("The generated acceptance criteria are draft quality and require stakeholder review.")
        return assumptions

    def _build_clarification_questions(
        self,
        story: dict[str, str | bool],
        user_input: str,
        product_context: dict[str, Any],
    ) -> list[str]:
        questions: list[str] = []
        lower = user_input.lower()
        if not story["explicit_role"]:
            questions.append("Who is the primary user or stakeholder for this workflow?")
        if not story["explicit_benefit"]:
            questions.append("What measurable business outcome should this story support?")
        if len(user_input.split()) < 8:
            questions.append("What trigger, input data, and success condition should define completion?")
        if "approval" in lower and "threshold" not in lower:
            questions.append("Are there approval thresholds, escalation paths, or delegated approver rules?")
        if "notification" in lower and "channel" not in lower:
            questions.append("Which notification channels and timing rules should be used?")
        if not product_context.get("constraints"):
            questions.append("Are there compliance, security, or operational constraints to account for?")
        return questions[:5]

    def _score_definition_of_ready(
        self,
        story: dict[str, str | bool],
        user_input: str,
        context: dict[str, Any],
        acceptance_criteria: list[AcceptanceCriteriaItem],
        edge_cases: list[str],
        backlog_items: list[dict[str, Any]],
    ) -> DefinitionOfReadyResult:
        lower = user_input.lower()
        checks = [
            ("Has user role", bool(story["explicit_role"])),
            ("Has clear goal", bool(story["goal"]) and len(str(story["goal"]).split()) >= 3),
            ("Has business value", bool(story["explicit_benefit"])),
            ("Has acceptance criteria", len(acceptance_criteria) >= 3),
            ("Has testable behavior", any(word in lower for word in ["reset", "approve", "receive", "notify", "build", "submit", "flow"])),
            ("Has dependencies/context", bool(context.get("constraints")) or bool(backlog_items)),
            ("Has edge cases", len(edge_cases) >= 3),
        ]
        passed = [label for label, result in checks if result]
        failed = [label for label, result in checks if not result]
        score = round((len(passed) / len(checks)) * 100)
        return DefinitionOfReadyResult(score=score, passed=passed, failed=failed)

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
