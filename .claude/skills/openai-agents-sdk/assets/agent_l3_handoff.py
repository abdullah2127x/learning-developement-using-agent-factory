"""
Level 3: Multi-Agent Orchestration — OpenAI Agents SDK
=======================================================
Three specialist agents + triage router with handoff pattern.

Requirements:
    pip install openai-agents

Environment:
    OPENAI_API_KEY set in .env
"""

import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


# ── Define specialist agents ───────────────────────────────────────────
billing_agent = Agent(
    name="Billing Agent",
    instructions=(
        "You handle all billing-related questions: invoices, payments, "
        "refunds, subscriptions. Be professional and empathetic."
    ),
    model="gpt-4o-mini",
)

technical_agent = Agent(
    name="Technical Agent",
    instructions=(
        "You handle all technical support: bugs, setup, errors, "
        "troubleshooting. Be clear and provide step-by-step solutions."
    ),
    model="gpt-4o-mini",
)

sales_agent = Agent(
    name="Sales Agent",
    instructions=(
        "You help with sales inquiries: pricing, features, packages, "
        "upgrades. Be enthusiastic and focus on value."
    ),
    model="gpt-4o-mini",
)


# ── Define triage agent (routes to specialists) ────────────────────────
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a customer support router. Route incoming questions to the "
        "right specialist:\n"
        "- Billing Agent: invoices, payments, refunds, subscriptions\n"
        "- Technical Agent: bugs, errors, setup, troubleshooting\n"
        "- Sales Agent: pricing, features, upgrades\n"
        "- Handle general greetings yourself.\n"
        "\n"
        "Use handoffs to delegate to specialists."
    ),
    handoffs=[billing_agent, technical_agent, sales_agent],
    model="gpt-4o-mini",
)


# ── Run ────────────────────────────────────────────────────────────────
async def main():
    user_input = input("Customer: ").strip()
    result = await Runner.run(triage_agent, user_input)
    print(f"Response: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
