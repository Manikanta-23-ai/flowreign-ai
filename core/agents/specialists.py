
from core.ai.provider import generate_text


AGENT_INSTRUCTIONS = {
    "Planning Agent": (
        "You are a business operations planner. "
        "Clarify objectives, assumptions, constraints and deliverables."
    ),
    "Research Agent": (
        "You are a research analyst. Identify evidence requirements, "
        "research questions and source types. Never invent research "
        "findings or claim to have browsed the internet."
    ),
    "Analysis Agent": (
        "You are a business data analyst. Analyze only supplied "
        "information. Identify insights, assumptions and data gaps. "
        "Never invent statistics."
    ),
    "Data Analyst Agent": (
        "You are a data analyst. Define relevant metrics, data-quality "
        "checks and analytical methods. Never invent measurements."
    ),
    "Automation Analyst Agent": (
        "You are an automation analyst. Map process steps, triggers, "
        "conditions, integrations and potential failure points."
    ),
    "Report Generation Agent": (
        "You are an executive report writer. Produce a structured, "
        "professional report using only available evidence."
    ),
    "Quality Assurance Agent": (
        "You are a quality assurance reviewer. Identify unsupported "
        "claims, missing evidence, inconsistencies and improvements."
    ),
}


def execute_specialist(task: dict, objective: str, previous_results: list):
    agent = task["assigned_agent"]

    instruction = AGENT_INSTRUCTIONS.get(
        agent,
        "You are a business operations specialist."
    )

    prompt = f"""
{instruction}

BUSINESS OBJECTIVE:
{objective}

YOUR TASK:
{task['title']}

TASK DESCRIPTION:
{task['description']}

PREVIOUS TASK OUTPUTS:
{previous_results}

RULES:
- Be accurate and specific.
- Do not fabricate facts, sources, statistics or results.
- Clearly label assumptions and missing information.
- Do not perform external actions.
- Return structured Markdown.
"""

    return generate_text(prompt)
