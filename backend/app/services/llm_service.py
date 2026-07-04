import re
from typing import Any

from app.schemas.agent import (
    AcceptanceCriteriaItem,
    AcceptanceCriteriaOutput,
    DORCheckOutput,
    DORFailedCheck,
    DORPassedCheck,
    DecomposedUserStory,
    DefinitionOfReadyResult,
    EpicDecompositionOutput,
    InvestCheck,
    ReleaseSlice,
)


class MockLLMService:
    def generate(
        self,
        task: str,
        user_input: str,
        product_context: dict[str, Any],
        backlog_items: list[dict[str, Any]],
    ) -> str | AcceptanceCriteriaOutput | EpicDecompositionOutput | DORCheckOutput:
        if task == "draft_acceptance_criteria":
            return self._draft_acceptance_criteria(user_input, product_context, backlog_items)
        if task == "decompose_epic":
            return self._decompose_epic(user_input, product_context, backlog_items)
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

    def _decompose_epic(
        self,
        user_input: str,
        product_context: dict[str, Any],
        backlog_items: list[dict[str, Any]],
    ) -> EpicDecompositionOutput:
        lower = user_input.lower()
        is_procurement = any(term in lower for term in ["purchase order", "procurement", "supplier", "vendor"])
        is_vague = self._is_vague_input(user_input)
        personas = self._epic_personas(lower)
        epic_summary = self._summarize_epic(user_input, product_context)
        stories = self._build_decomposed_stories(personas, is_procurement, is_vague)
        release_slices = [
            ReleaseSlice(
                name="MVP",
                stories=["US-1", "US-2", "US-3"],
                rationale="Delivers the core submit, review, and decision workflow needed to validate the product value.",
            ),
            ReleaseSlice(
                name="Later enhancement",
                stories=["US-4"],
                rationale="Adds proactive visibility after the core approval path is proven.",
            ),
            ReleaseSlice(
                name="Operational/admin",
                stories=["US-5"],
                rationale="Gives administrators control over thresholds and routing rules after MVP behavior is stable.",
            ),
        ]
        if len(stories) > 5:
            release_slices.append(
                ReleaseSlice(
                    name="Compliance hardening",
                    stories=["US-6"],
                    rationale="Captures audit and exception reporting once the end-to-end workflow is understood.",
                )
            )

        open_questions = self._build_epic_open_questions(lower, is_vague)
        assumption_heavy = is_vague or len(open_questions) >= 3
        compliance_or_approval = any(term in lower for term in ["approval", "approve", "compliance", "security", "procurement"])
        human_review_required = assumption_heavy or compliance_or_approval
        review_reason = (
            "Human review is required because the epic includes approval or procurement workflow decisions and unresolved assumptions."
            if human_review_required
            else "The epic is decomposed with low ambiguity, but Product Owner review is still recommended before backlog commitment."
        )
        return EpicDecompositionOutput(
            epic_summary=epic_summary,
            decomposed_user_stories=stories,
            release_slices=release_slices,
            open_questions=open_questions,
            human_review_required=human_review_required,
            review_reason=review_reason,
        )

    def _epic_personas(self, lower_text: str) -> dict[str, str]:
        if "procurement" in lower_text or "purchase order" in lower_text:
            return {
                "requester": "procurement requester",
                "approver": "finance manager",
                "admin": "procurement administrator",
                "observer": "enterprise procurement lead",
            }
        return {
            "requester": "business user",
            "approver": "workflow approver",
            "admin": "system administrator",
            "observer": "Product Owner",
        }

    def _summarize_epic(self, user_input: str, product_context: dict[str, Any]) -> str:
        target_user = product_context.get("target_user", "Technical Product Owner")
        return (
            f"Decompose '{self._clean_phrase(user_input)}' into sprint-sized stories for a {target_user}, "
            "with emphasis on business value, workflow clarity, and review checkpoints."
        )

    def _build_decomposed_stories(
        self,
        personas: dict[str, str],
        is_procurement: bool,
        is_vague: bool,
    ) -> list[DecomposedUserStory]:
        domain_object = "purchase order" if is_procurement else "request"
        stories = [
            self._story(
                story_id="US-1",
                title=f"Submit {domain_object} for approval",
                persona=personas["requester"],
                goal=f"to submit a {domain_object} with required details",
                value="approval can begin with complete and consistent information",
                priority="High",
                complexity="M",
                dependencies=["Required fields and validation rules", "Requester permissions"],
                risks=["Incomplete submission rules may create rework"],
            ),
            self._story(
                story_id="US-2",
                title=f"Review and decide on {domain_object}",
                persona=personas["approver"],
                goal=f"to approve, reject, or request changes for a {domain_object}",
                value="spend decisions are controlled before commitment",
                priority="High",
                complexity="M",
                dependencies=["Approval policy", "Decision states", "Approver assignment"],
                risks=["Approval thresholds may differ by department or amount"],
            ),
            self._story(
                story_id="US-3",
                title="Track workflow status",
                persona=personas["requester"],
                goal=f"to see the current status of my {domain_object}",
                value="I know whether action is needed and can plan follow-up",
                priority="High",
                complexity="S",
                dependencies=["Workflow state model", "Notification rules"],
                risks=["Status labels may be interpreted differently across teams"],
            ),
            self._story(
                story_id="US-4",
                title="Notify stakeholders about delays and decisions",
                persona=personas["observer"],
                goal=f"to receive notifications when a {domain_object} is delayed or decided",
                value="teams can respond before procurement risk affects delivery",
                priority="Medium",
                complexity="M",
                dependencies=["Notification channels", "Delay thresholds", "Recipient rules"],
                risks=["Too many notifications may reduce trust in the workflow"],
            ),
            self._story(
                story_id="US-5",
                title="Configure approval rules",
                persona=personas["admin"],
                goal="to configure approvers, thresholds, and escalation paths",
                value="the workflow can reflect enterprise policy without code changes",
                priority="Medium",
                complexity="L",
                dependencies=["Role model", "Policy ownership", "Audit requirements"],
                risks=["Rule complexity may make the MVP too large"],
            ),
        ]
        if is_vague:
            stories.append(
                self._story(
                    story_id="US-6",
                    title="Capture workflow assumptions for review",
                    persona="Product Owner",
                    goal="to document unresolved workflow assumptions",
                    value="stakeholders can validate scope before delivery starts",
                    priority="High",
                    complexity="S",
                    dependencies=["Stakeholder availability", "Discovery notes"],
                    risks=["Unvalidated assumptions may create churn during refinement"],
                    force_review_note="Assumption-heavy story should be refined before sprint planning.",
                )
            )
        return stories

    def _story(
        self,
        story_id: str,
        title: str,
        persona: str,
        goal: str,
        value: str,
        priority: str,
        complexity: str,
        dependencies: list[str],
        risks: list[str],
        force_review_note: str | None = None,
    ) -> DecomposedUserStory:
        invest_notes = [
            "Story has a distinct persona and outcome.",
            "Acceptance criteria preview makes behavior testable.",
        ]
        small = complexity != "L"
        if not small:
            invest_notes.append("Large complexity suggests this may need further splitting.")
        if force_review_note:
            invest_notes.append(force_review_note)

        return DecomposedUserStory(
            id=story_id,
            title=title,
            user_story=f"As a {persona}, I want {goal}, so that {value}.",
            persona=persona,
            goal=goal,
            business_value=value,
            acceptance_criteria_preview=[
                f"Given a {persona} has access, When they start this story workflow, Then the system shows the required action.",
                "Given valid information is provided, When the user submits, Then the system records the outcome and updates status.",
                "Given information is missing or invalid, When the user attempts to continue, Then the system explains what must be corrected.",
            ],
            priority=priority,  # type: ignore[arg-type]
            estimated_complexity=complexity,  # type: ignore[arg-type]
            dependencies=dependencies,
            risks=risks,
            invest_check=InvestCheck(
                independent=True,
                negotiable=True,
                valuable=True,
                estimable=bool(dependencies),
                small=small,
                testable=True,
                notes=invest_notes,
            ),
        )

    def _build_epic_open_questions(self, lower_text: str, is_vague: bool) -> list[str]:
        questions: list[str] = []
        if is_vague:
            questions.append("Which persona and workflow should be prioritized for the first release?")
            questions.append("What measurable business outcome defines a better experience?")
        if "approval" in lower_text or "approve" in lower_text:
            questions.append("What approval thresholds, escalation paths, and delegated approver rules are required?")
        if "procurement" in lower_text or "purchase order" in lower_text:
            questions.append("Which procurement systems or supplier records does the workflow depend on?")
        questions.append("Which audit, compliance, or reporting obligations must be met before production use?")
        return questions[:5]

    def _is_vague_input(self, user_input: str) -> bool:
        lower = user_input.lower()
        vague_terms = ["improve", "better", "experience", "optimize", "modernize"]
        return len(user_input.split()) < 7 or any(term in lower for term in vague_terms)

    def _check_dor(self, user_input: str) -> DORCheckOutput:
        lower = user_input.lower()
        story = self._parse_or_rewrite_story(user_input)
        checks = [
            (
                "User persona defined",
                bool(story["explicit_role"]),
                "The item names the user or stakeholder who receives value.",
                "Add the primary user persona using 'As a [persona]'.",
            ),
            (
                "Goal defined",
                bool(story["goal"]) and len(str(story["goal"]).split()) >= 3,
                "The desired action or outcome is understandable.",
                "Clarify the workflow, action, or capability the user needs.",
            ),
            (
                "Business value defined",
                bool(story["explicit_benefit"]),
                "The item explains why the outcome matters.",
                "Add the benefit using 'so that [business value]'.",
            ),
            (
                "Acceptance criteria present",
                any(term in lower for term in ["given", "when", "then", "acceptance criteria", "ac-"]),
                "Acceptance criteria or test examples are included.",
                "Add 3 to 5 Given/When/Then acceptance criteria.",
            ),
            (
                "Dependencies mentioned",
                any(term in lower for term in ["depends", "dependency", "integrates", "system", "api", "approval", "procurement"]),
                "The item mentions relevant dependencies or workflow relationships.",
                "Identify upstream systems, roles, policies, or data dependencies.",
            ),
            (
                "Edge cases considered",
                any(term in lower for term in ["edge", "invalid", "missing", "exception", "error", "reject"]),
                "The item considers alternate or failure paths.",
                "Document invalid, missing, duplicate, and exception scenarios.",
            ),
            (
                "Non-functional needs mentioned",
                any(term in lower for term in ["performance", "security", "audit", "compliance", "accessibility", "latency"]),
                "The item names at least one non-functional concern.",
                "Add auditability, security, performance, or accessibility expectations.",
            ),
            (
                "Testability is clear",
                any(term in lower for term in ["approve", "reject", "reset", "receive", "notify", "submit", "track", "view"]),
                "The behavior can be verified through observable outcomes.",
                "Make the expected system behavior observable and testable.",
            ),
            (
                "Scope is small enough",
                len(user_input.split()) <= 35 and not any(term in lower for term in ["system", "platform", "experience", "end-to-end"]),
                "The item appears small enough for refinement.",
                "Split broad platform or experience work into smaller stories.",
            ),
            (
                "Ambiguity is low",
                not self._is_vague_input(user_input),
                "The wording is specific enough for team discussion.",
                "Replace vague wording with concrete actors, triggers, rules, and outcomes.",
            ),
        ]

        passed = [
            DORPassedCheck(check=label, reason=passed_reason)
            for label, result, passed_reason, _ in checks
            if result
        ]
        failed = [
            DORFailedCheck(check=label, reason="This readiness signal is missing or weak.", recommendation=recommendation)
            for label, result, _, recommendation in checks
            if not result
        ]
        dor_score = round((len(passed) / len(checks)) * 100)
        if dor_score >= 80:
            status = "Ready"
        elif dor_score >= 50:
            status = "Needs Refinement"
        else:
            status = "Not Ready"

        risk_flags = self._dor_risk_flags(lower, failed)
        recommended_next_actions = [item.recommendation for item in failed[:4]]
        if not recommended_next_actions:
            recommended_next_actions.append("Review with the delivery team and confirm estimates before sprint commitment.")

        human_review_required = status != "Ready" or bool(risk_flags)
        if human_review_required:
            review_reason = (
                f"Human review required because the item status is {status} with "
                f"{len(failed)} readiness gap(s) and {len(risk_flags)} risk flag(s)."
            )
        else:
            review_reason = "No major DoR gaps detected by the mock checks; Product Owner review is still recommended."

        return DORCheckOutput(
            item_summary=self._clean_phrase(user_input),
            dor_score=dor_score,
            status=status,  # type: ignore[arg-type]
            passed_checks=passed,
            failed_checks=failed,
            risk_flags=risk_flags,
            recommended_next_actions=recommended_next_actions,
            human_review_required=human_review_required,
            review_reason=review_reason,
        )

    def _dor_risk_flags(self, lower_text: str, failed: list[DORFailedCheck]) -> list[str]:
        flags: list[str] = []
        if any(term in lower_text for term in ["approval", "approve", "procurement", "finance"]):
            flags.append("Approval or finance workflow may require policy and audit validation.")
        if any(term in lower_text for term in ["security", "compliance", "audit"]):
            flags.append("Compliance-sensitive requirements should be reviewed before implementation.")
        if any(item.check == "Scope is small enough" for item in failed):
            flags.append("Scope may be too broad for a single sprint-ready story.")
        if any(item.check == "Ambiguity is low" for item in failed):
            flags.append("Ambiguous wording may cause delivery churn during refinement.")
        return flags
