# Research desk — Streamlit UI for a LangChain agent with web search + weather tools.
# Run with:  streamlit run app.py

import json
import os

import certifi
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

# ============================================
# PAGE CONFIG (must be the first st.* call)
# ============================================
st.set_page_config(page_title="Research desk", page_icon="🌦️", layout="centered")

# ============================================
# ENVIRONMENT
# ============================================
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

SYSTEM_PROMPT = """
You are a helpful research assistant.
Use search for current factual information.
Use the weather tool for current weather.
Do not invent tool results.
Answer in clear, well-structured Markdown.
"""

SUGGESTIONS = [
    "Find the capital of Switzerland and its current weather",
    "What's the weather in Tokyo right now, and what's on there this week?",
    "Compare today's weather in Seoul and Busan",
]

# Friendly names for the tool trace: tool name -> (label, arg to show)
TOOL_LABELS = {
    "tavily_search": ("Searched the web", "query"),
    "get_weather_data": ("Checked weather", "city"),
}


# ============================================
# TOOLS
# ============================================
@tool
def get_weather_data(city: str) -> str:
    """Fetch the current weather for a city. Input: a city name, e.g. 'Bern'."""
    try:
        response = requests.get(
            "http://api.weatherstack.com/current",
            params={"access_key": WEATHERSTACK_API_KEY, "query": city},  # requests URL-encodes these
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        # Don't return str(exc): it contains the full URL, including the API key.
        return f"Weather service unreachable for {city} ({type(exc).__name__})."

    if "current" not in data:
        reason = data.get("error", {}).get("info", "unknown error")
        return f"Could not fetch weather for {city}: {reason}"

    current = data["current"]
    location = data.get("location", {})
    conditions = ", ".join(current.get("weather_descriptions", [])) or "n/a"
    return (
        f"City: {location.get('name', city)}, {location.get('country', '')}\n"
        f"Local time: {location.get('localtime', 'n/a')}\n"
        f"Temperature: {current.get('temperature')} °C "
        f"(feels like {current.get('feelslike')} °C)\n"
        f"Conditions: {conditions}\n"
        f"Humidity: {current.get('humidity')}%, wind: {current.get('wind_speed')} km/h"
    )


# ============================================
# AGENT (built once per model/temperature, reused across reruns)
# ============================================
@st.cache_resource(show_spinner=False)
def build_agent(model_name: str, temperature: float):
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        api_key=GOOGLE_API_KEY,
    )
    tools = [TavilySearch(max_results=2), get_weather_data]
    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


# ============================================
# HELPERS
# ============================================
def message_text(message) -> str:
    """Gemini may return content as a plain string OR as a list of content blocks."""
    content = message.content
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


def describe_call(name: str, args: dict) -> str:
    label, key = TOOL_LABELS.get(name, (f"Used {name}", None))
    detail = args.get(key) if key else json.dumps(args, ensure_ascii=False)
    return f"{label}: {detail}"


def render_step(step: dict) -> None:
    st.markdown(f"**{describe_call(step['tool'], step['args'])}**")
    output = step.get("output")
    if output is None:
        return
    if step["tool"] == "tavily_search":
        try:
            results = json.loads(output).get("results", [])
            for r in results:
                st.markdown(f"- [{r.get('title', 'Untitled')}]({r.get('url')})")
            return
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
    st.code(output[:1500], language=None)


def trace_label(steps: list) -> str:
    n = len(steps)
    if n == 0:
        return "Answered without tools"
    return f"Used {n} tool{'s' if n > 1 else ''}"


def run_agent(agent, history: list, status) -> tuple[str, list]:
    """Stream the agent graph and draw each tool call as it happens."""
    steps, by_id, final = [], {}, ""
    for chunk in agent.stream(
        {"messages": history},
        stream_mode="updates",  # one chunk per graph node (model / tools)
        config={"recursion_limit": 12},  # safety cap on the think→act loop
    ):
        for update in chunk.values():
            if not isinstance(update, dict):
                continue
            for msg in update.get("messages", []):
                if isinstance(msg, AIMessage):
                    for call in msg.tool_calls:
                        step = {"tool": call["name"], "args": call.get("args", {}), "output": None}
                        steps.append(step)
                        by_id[call["id"]] = step
                        status.update(label=describe_call(step["tool"], step["args"]) + "…")
                    if not msg.tool_calls:
                        final = message_text(msg)
                elif isinstance(msg, ToolMessage):
                    step = by_id.get(msg.tool_call_id)
                    if step is not None:
                        content = msg.content
                        step["output"] = content if isinstance(content, str) else json.dumps(content)
                        with status:
                            render_step(step)
    return final, steps


# ============================================
# STYLE
# ============================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

.stApp, .stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stChatInput"] textarea, .stButton button p {
  font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
}
.stMarkdown p, .stMarkdown li { line-height: 1.6; }

.masthead { position: relative; padding: 2.25rem 0 1.5rem; margin-bottom: 0.5rem; }
.masthead svg { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 0; }
.masthead svg path { fill: none; stroke: #2F6F8F; stroke-width: 1; opacity: 0.22; }
.masthead .title {
  position: relative; z-index: 1;
  font-family: 'Newsreader', Georgia, serif; font-weight: 600;
  font-size: clamp(2.4rem, 6vw, 3.4rem); line-height: 1.05; letter-spacing: -0.02em;
  color: #1C2B36;
}
.masthead .lede {
  position: relative; z-index: 1; max-width: 34rem; margin-top: 0.6rem;
  font-size: 1.02rem; line-height: 1.55; color: #4A5D69;
}

[data-testid="stChatMessage"] { background: transparent; padding: 0.9rem 0.25rem; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: #E1E8EA; border-radius: 14px; padding: 0.9rem 1rem;
}
[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3 { font-family: 'Newsreader', Georgia, serif; }

[data-testid="stExpander"] details, [data-testid="stStatusWidget"] {
  border-color: #C9D5D9; background: #F6F8F9;
}

.stButton button {
  text-align: left; border: 1px solid #C9D5D9; background: #F6F8F9;
  border-radius: 10px; min-height: 4.5rem; width: 100%;
}
.stButton button:hover { border-color: #2F6F8F; color: #2F6F8F; }
.stButton button:focus-visible { outline: 2px solid #2F6F8F; outline-offset: 2px; }

[data-testid="stSidebar"] { background: #E1E8EA; }
.key-row { font-size: 0.9rem; margin: 0.15rem 0; color: #4A5D69; }
.key-row b { color: #1C2B36; font-weight: 500; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.subheader("Settings")
    model_name = st.selectbox("Model", ["gemini-3.8-flash"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05,
                            help="Lower is more deterministic.")

    st.subheader("API keys")
    for label, value in [("Google", GOOGLE_API_KEY), ("Tavily", TAVILY_API_KEY),
                         ("Weatherstack", WEATHERSTACK_API_KEY)]:
        mark = "✓ found" if value else "✗ missing in .env"
        st.markdown(f"<div class='key-row'><b>{label}</b> — {mark}</div>",
                    unsafe_allow_html=True)

    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ============================================
# HEADER
# ============================================
st.markdown(
    """
<div class="masthead">
<svg viewBox="0 0 600 170" preserveAspectRatio="none" aria-hidden="true">
<path d="M-20 150 C 100 90, 230 170, 360 110 S 560 60, 640 80"/>
<path d="M-20 125 C 110 65, 240 145, 370 85 S 570 35, 640 55"/>
<path d="M-20 100 C 120 40, 250 120, 380 60 S 580 10, 640 30"/>
<path d="M-20 75 C 130 15, 260 95, 390 35 S 590 -15, 640 5"/>
</svg>
<div class="title">Research desk</div>
<div class="lede">Ask about any place. The assistant searches the web and reads live
weather before it answers, and shows you every source it used.</div>
</div>
""",
    unsafe_allow_html=True,
)

if not GOOGLE_API_KEY:
    st.error("Add GOOGLE_API_KEY to your .env file, then restart the app.")
    st.stop()

# ============================================
# CHAT STATE
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []  # each: {"role", "content", "steps"}

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🌦️" if m["role"] == "assistant" else None):
        if m.get("steps") is not None:
            with st.expander(trace_label(m["steps"])):
                for step in m["steps"]:
                    render_step(step)
        st.markdown(m["content"])

prompt = st.chat_input("Ask about a place, a fact, or the weather")

# Starter prompts on an empty conversation
suggestion_slot = st.empty()
if not st.session_state.messages and not prompt:
    with suggestion_slot.container():
        st.caption("Try one of these")
        cols = st.columns(len(SUGGESTIONS))
        for col, text in zip(cols, SUGGESTIONS):
            if col.button(text, key=f"sugg-{text}"):
                prompt = text

# ============================================
# HANDLE A NEW QUESTION
# ============================================
if prompt:
    suggestion_slot.empty()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # The agent itself is stateless between calls: we send the full history every time.
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.messages if m["content"]]

    with st.chat_message("assistant", avatar="🌦️"):
        try:
            agent = build_agent(model_name, temperature)
            with st.status("Thinking…", expanded=False) as status:
                answer, steps = run_agent(agent, history, status)
                status.update(label=trace_label(steps), state="complete")
        except Exception as exc:
            st.session_state.messages.pop()  # drop the unanswered question
            st.error(f"The agent stopped with an error: {type(exc).__name__}: {exc}")
            st.stop()

        answer = answer or "_The model returned an empty answer. Try rephrasing._"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer, "steps": steps})