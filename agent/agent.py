"""
THE AGENT BRAIN - TaskPilot's ReAct Loop

Flow:
1. User says something ("Add buy milk to my list")
2. LLM sees available tools and DECIDES what to do
3. If tool needed → execute it → feed result back to LLM
4. LLM checks: "Am I done? Or do I need more tool calls?"
5. Keeps looping until the LLM is satisfied
6. LLM gives a natural language response

This LOOP is what makes it AGENTIC — not a single call, but
the agent keeps going until the job is fully done.
"""

import json
from groq import Groq
from taskpilot.core.config import settings
from taskpilot.agent.tools import TOOL_DEFINITIONS, execute_tool

client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """You are TaskPilot, a helpful AI task manager.
You help users manage their to-do list using your tools.

Available actions:
- Create new tasks
- List all tasks
- Mark tasks as complete
- Delete tasks

Use tools when the user wants to manage tasks.
If they just want to chat or ask questions, respond normally.
Be concise and friendly."""

MAX_ITERATIONS = 10  # Safety limit to prevent infinite loops


def run_agent(user_message: str) -> dict:
    """
    Run the agent loop (ReAct pattern).

    The agent keeps calling tools until it's satisfied the task
    is fully complete. This is what makes it agentic — it doesn't
    stop after one tool call if the job isn't done yet.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    tools_used = []
    iterations = 0

    # THE AGENTIC LOOP — keeps going until the job is done
    while iterations < MAX_ITERATIONS:
        iterations += 1
        print(f"\n🔄 Agent loop iteration {iterations}")

        # Ask the LLM (with tools available)
        response = client.chat.completions.create(
            model=settings.MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1024,
        )

        assistant_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # If NO tool calls — the agent is done thinking/acting
        if not assistant_message.tool_calls:
            print("✅ Agent finished — no more tools needed")
            break

        # The agent wants to ACT — execute all requested tools
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"  🔧 Calling: {tool_name}({tool_args})")

            # Execute the tool
            tool_result = execute_tool(tool_name, tool_args)

            tools_used.append({
                "tool": tool_name,
                "input": tool_args,
                "output": json.loads(tool_result)
            })

            # Feed result back to LLM so it can observe
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # If the LLM stopped naturally, it's satisfied
        if finish_reason == "stop":
            print("✅ Agent satisfied (finish_reason=stop)")
            break

        # Otherwise, loop again — the agent needs more iterations
        print(f"  ↩️  Agent not done yet (finish_reason={finish_reason}), looping...")

    # Get the final response
    # If the last message was tool results, ask LLM for a final summary
    if tools_used and (not assistant_message.content):
        final_response = client.chat.completions.create(
            model=settings.MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        final_answer = final_response.choices[0].message.content
    else:
        final_answer = assistant_message.content

    print(f"\n📊 Agent used {len(tools_used)} tool calls in {iterations} iterations")

    return {
        "response": final_answer,
        "tools_used": tools_used
    }
