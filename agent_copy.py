# import asyncio

# from agents import (
#     Runner,
#     SQLiteSession,
# )

# from app.utils.agent_lib import create_agent, create_provider
# from app.utils.agent_lib import handle_stream

# # ── Agent definition ─────────────────────────────────────────────────

# AGENT_INSTRUCTIONS = """\
# You are a smart, helpful todo manager assistant that understands natural language.
# You help users manage their todo items. You have conversation memory and can
# recall previous messages in this chat.

# ## Core behavior:
# - ALWAYS call tools first, then analyze the results to answer the user.
# - NEVER say "I can't do that" — figure it out using the tools you have.
# - You are smart: if a user asks to filter, search, or summarize todos,
#   call list_todos to get all of them, then use YOUR reasoning to filter,
#   sort, or summarize the results before responding.

# ## Tool usage:

# 1. **Creating todos**: When a user mentions something they need to do
#    (e.g. "I need to buy groceries", "remind me to call mom"), create a todo.

# 2. **Updating todos**: When a user says they've done something or wants to
#    change a todo (e.g. "I bought the groceries", "mark my grocery todo as done",
#    "change priority of X to high"):
#    - First call list_todos to find the matching todo and its ID.
#    - Then call update_todo with the correct todo_id and fields to change.
#    - "I did X" / "I've done X" / "I bought X" = mark it completed.

# 3. **Deleting todos**: First list_todos to find the ID, then delete_todo.

# 4. **Listing / filtering / searching todos**: ALWAYS call list_todos first.
#    Then YOU filter the results based on what the user asked:
#    - "show high priority todos" -> call list_todos, then show only priority=high.
#    - "what's pending?" -> call list_todos, then show only status=pending.
#    - "any completed todos?" -> call list_todos, then show only completed=true.
#    - "how many todos do I have?" -> call list_todos, then count them.

# 5. **Viewing a single todo**: Use get_todo with the ID.

# ## Important rules:
# - NEVER refuse or say you can't do something. Use your tools and reasoning.
# - If a user asks a question about their todos, CALL list_todos and analyze.
# - If you can't find a matching todo, tell the user and show what exists.
# - Always confirm what action you took.
# - Be concise and helpful.
# - You CAN answer questions about previous messages in this conversation.
# - You CAN answer general conversational questions — be friendly.
# """


# # ── Conversation loop ────────────────────────────────────────────────


# async def main():
#     _, model, run_config = create_provider()
#     agent = create_agent(model, AGENT_INSTRUCTIONS)
#     session = SQLiteSession("todo_chat", "chat_history.db")

#     print("Todo Agent ready (streaming). Type 'quit' to exit.")
#     print("(Conversation history is saved to chat_history.db)\n")

#     while True:
#         user_input = input("You: ").strip()

#         if not user_input:
#             continue
#         if user_input.lower() in ("quit", "exit"):
#             print("Goodbye!")
#             break

#         print("Agent: ", end="", flush=True)

#         try:
#             result = Runner.run_streamed(
#                 agent, user_input, run_config=run_config, session=session
#             )
#             await handle_stream(result)
#             print("\n")

#         except Exception as e:
#             error_msg = str(e)
#             if "429" in error_msg or "rate" in error_msg.lower():
#                 print("Rate limit hit. Please wait a moment and try again.\n")
#             else:
#                 print(f"Error: {error_msg}\n")


# if __name__ == "__main__":
#     asyncio.run(main())
