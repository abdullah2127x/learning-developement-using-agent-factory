"""
Level 3: Agent-as-Tool Orchestrator — OpenAI Agents SDK
========================================================
Orchestrator agent that calls specialist sub-agents as tools.
Main agent KEEPS CONTROL — unlike handoffs where control transfers.

How it works:
  1. agent.as_tool() wraps each sub-agent as a FunctionTool
  2. The LLM sees them as regular tools (name + description)
  3. When called, the sub-agent receives ONLY generated input (not conversation history)
  4. The orchestrator receives the sub-agent's output as a tool result
  5. The orchestrator combines results and decides what to do next

Pattern comparison:
  - Handoff (agent_l3_handoff.py): control transfers permanently → specialist finishes
  - Agent-as-Tool (this file): main agent stays in control → calls tools → combines results
  - Runner-inside-tool: maximum control → Runner.run() inside @function_tool

Requirements:
    pip install openai-agents

Environment:
    OPENAI_API_KEY set in .env
"""

import asyncio

from agents import Agent, Runner, function_tool


# ── Specialist Sub-Agents ─────────────────────────────────────────────
# Each specialist is a standalone agent. They don't know about each other.
# The orchestrator decides when to call them and how to use their output.

spanish_agent = Agent(
    name="Spanish Translator",
    instructions="Translate the user's message to Spanish. Return only the translation, nothing else.",
    model="gpt-4o-mini",
)

french_agent = Agent(
    name="French Translator",
    instructions="Translate the user's message to French. Return only the translation, nothing else.",
    model="gpt-4o-mini",
)

summarizer_agent = Agent(
    name="Summarizer",
    instructions="Summarize the provided text in one concise sentence. Return only the summary.",
    model="gpt-4o-mini",
)


# ── Runner-inside-Tool (maximum control pattern) ─────────────────────
# For cases where as_tool() isn't enough: custom error handling, retries,
# conditional logic, or metadata tracking.

@function_tool
async def research_topic(topic: str) -> str:
    """Research a topic in depth and return a brief report."""
    research_agent = Agent(
        name="Researcher",
        instructions=(
            "You are a research assistant. Given a topic, provide a clear, "
            "factual 2-3 sentence overview. Be concise and accurate."
        ),
        model="gpt-4o-mini",
    )
    result = await Runner.run(
        research_agent,
        f"Research this topic: {topic}",
        max_turns=3,
    )
    return str(result.final_output)


# ── Orchestrator (main agent — stays in control) ─────────────────────
# The orchestrator sees sub-agents as tools. It decides:
#   - WHEN to call them (based on user request)
#   - WHAT input to send (generated, not full history)
#   - HOW to combine results (in its final response)

orchestrator = Agent(
    name="Orchestrator",
    instructions=(
        "You are a multilingual assistant and coordinator.\n"
        "You have access to specialist tools:\n"
        "- translate_to_spanish: translate text to Spanish\n"
        "- translate_to_french: translate text to French\n"
        "- summarize_text: summarize any text concisely\n"
        "- research_topic: research any topic and get a brief report\n\n"
        "Use the appropriate tools based on the user's request. "
        "You can call multiple tools and combine their results. "
        "Always present the final answer clearly to the user."
    ),
    tools=[
        # as_tool() pattern — wraps agent as a FunctionTool
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate text to Spanish.",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate text to French.",
        ),
        summarizer_agent.as_tool(
            tool_name="summarize_text",
            tool_description="Summarize a block of text into one sentence.",
        ),
        # Runner-inside-tool pattern — manual Runner.run() for full control
        research_topic,
    ],
    model="gpt-4o-mini",
)


# ── Run ───────────────────────────────────────────────────────────────
async def main():
    print("=== Agent-as-Tool Orchestrator ===\n")
    print("Try: 'Translate hello world to Spanish and French'")
    print("Try: 'Research quantum computing and summarize it'")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "quit":
            print("Goodbye!")
            break

        result = await Runner.run(orchestrator, user_input, max_turns=15)
        print(f"\nOrchestrator: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
