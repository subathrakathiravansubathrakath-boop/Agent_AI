import os
import json
import datetime
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Agent & Automation", page_icon="🤖", layout="wide")
st.title("🤖 AI Agent: Tools & Automation")
st.write("A simple tool-using agent that understands a task, chooses a tool, processes the result, and responds.")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("OpenAI API key", type="password")
model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4.1-mini"], index=0)
max_steps = st.sidebar.slider("Maximum tool steps", min_value=1, max_value=5, value=3)
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None
    st.sidebar.info("Enter your API key to enable AI planning. The demo tools below are local and do not need an API key.")

# Safe demo tools: no arbitrary code execution, file access, or external side effects.
def calculator(expression: str) -> str:
    """Calculate a basic arithmetic expression."""
    allowed = set("0123456789+-*/(). %")
    if not expression or any(ch not in allowed for ch in expression):
        return "Error: only basic arithmetic characters are allowed."
    try:
        # Restricted builtins; expression has already been character-checked.
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception:
        return "Error: could not calculate that expression."

def get_current_date() -> str:
    """Return today's date."""
    return datetime.date.today().strftime("%A, %d %B %Y")

def word_count(text: str) -> str:
    """Count words and characters in text."""
    return json.dumps({"words": len(text.split()), "characters": len(text)})

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate a basic arithmetic expression such as (12 + 5) * 3.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Basic arithmetic expression"}},
                "required": ["expression"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current date.",
            "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": "Count words and characters in a piece of text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Text to count"}},
                "required": ["text"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

def execute_tool(name, arguments):
    if name == "calculator":
        return calculator(arguments.get("expression", ""))
    if name == "get_current_date":
        return get_current_date()
    if name == "word_count":
        return word_count(arguments.get("text", ""))
    return "Error: unknown tool."

def run_agent(task, model_name, step_limit):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI agent. Use tools when useful, especially for calculations, "
                "the current date, and word counts. Explain results clearly. Never claim a tool was "
                "used unless it was called. If the task is unsafe or outside available tools, explain limits."
            )
        },
        {"role": "user", "content": task}
    ]
    trace = []
    for _ in range(step_limit):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content or "I couldn't produce a response.", trace
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in message.tool_calls
            ]
        })
        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(tc.function.name, args)
            trace.append({"tool": tc.function.name, "arguments": args, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })
    # One final response without additional tool calls after reaching the step limit.
    messages.append({"role": "system", "content": "Tool-step limit reached. Respond using the results already available; do not call more tools."})
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content or "Task finished.", trace

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Try the AI Agent")
task = st.text_area(
    "Enter a task",
    placeholder="Examples:\n- Calculate (245 * 18) / 3\n- What is today's date?\n- Count the words in: AI agents can use tools to complete tasks.",
    height=120
)

col1, col2 = st.columns([1, 4])
with col1:
    run_button = st.button("▶ Run Agent", type="primary")
with col2:
    st.caption("Available tools: calculator, current date, and word/character counter.")

if run_button:
    if not task.strip():
        st.warning("Please enter a task.")
    elif not client:
        st.error("Enter your OpenAI API key in the sidebar to run the AI agent.")
    else:
        with st.spinner("Agent is planning and using tools..."):
            try:
                answer, trace = run_agent(task.strip(), model, max_steps)
                st.session_state.history.append({"task": task.strip(), "answer": answer, "trace": trace})
                st.subheader("Agent Response")
                st.write(answer)
                with st.expander("View agent tool-call trace"):
                    if trace:
                        for idx, item in enumerate(trace, 1):
                            st.markdown(f"**Step {idx}: `{item['tool']}`**")
                            st.json({"arguments": item["arguments"], "result": item["result"]})
                    else:
                        st.write("The agent answered without using a tool.")
            except Exception as exc:
                st.error(f"Agent error: {exc}")
                st.info("Check that your API key is valid and that your account has API access/billing enabled.")

if st.session_state.history:
    st.divider()
    st.subheader("Session History")
    for item in reversed(st.session_state.history):
        with st.expander(item["task"][:100]):
            st.markdown("**Answer**")
            st.write(item["answer"])
            if item["trace"]:
                st.markdown("**Tools used**")
                st.write(", ".join(x["tool"] for x in item["trace"]))
    if st.button("Clear session history"):
        st.session_state.history = []
        st.rerun()

st.divider()
st.markdown("""
### Agent workflow
**Understand Task → Decide Action → Use Tool → Process Result → Respond**

This demo uses a language model for planning and function calling, three bounded local tools, and Streamlit session state for chat/task history.
""")
