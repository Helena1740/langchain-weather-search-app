# %%
# ============================================
# PACKAGE INSTALLATIONS
# ============================================

import os # to talk to os, particularly to use env. vars
import certifi # gives trusted list of SSL certificates -> id for the website, tells that it can be trusted, lets Python to use this certificate bundle in HTTPS requests, network security setting
import requests # https calls
from dotenv import load_dotenv  # read env. variables from .env and load them into Python

from langchain_google_genai import ChatGoogleGenerativeAI # langchain wrapper around OpenAI models, langchain connection to OpenAI chat model
from langchain_tavily import TavilySearch
from langchain.tools import tool # to refine a finished program by adding a custom tool of weather info search
import streamlit as st

# %%
from langchain.agents import create_agent # we need to import some agents functionality, react -> agent has an ability to reason and perform actions

# %%


# %%
# ==========================
# LOAD ENVIRONMENT VARIABLES
# ==========================
os.environ["SSL_CERT_FILE"] = certifi.where() # uploads certified updates path instead of old one, may happen in Windows -> path issue
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # retrives the key, we do not put the secret directly into our source code
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

# %%
# =======================================
# SEARCH TOOL
# ======================================= better for agent to have tools
search_tool = TavilySearch(max_results=2)


# %%
# ============================
# WEATHER INFORMATION
# ============================
# custom tool, "take this normal Python function and expose it to the agent as a tool, without the decorator, it's just a Python function, but now LangChain knows the agent/LLM can call this function"
@tool
def get_weather_data(city: str) -> str:
    """Fetch the current weather information of the city""" # docstring in function as a tool helps agent to understand what the tool does, it matters a lot in agentic systems
    url= (
        f"http://api.weatherstack.com/current?"
        f"access_key={WEATHERSTACK_API_KEY}&query={city}"
    )
    response = requests.get(url) # it will give us a structured JSON file
    data = response.json() # Python converts to a dictionary-like object
    if "current" not in data:
        return f"Could not fetch weather data for {city}"
    return (
        f"City: {city}\n"
        f"Temperature: {data['current']['temperature']} degrees Celsius\n"
    )
        
    

# %%
# search_tool.invoke("What is the weather in Tokyo in October") # testing the tool, invoke = вызывать, вызов

# %%
# =======================================
# LLM
# =======================================
# the brain we use to ask questions

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash", # it's an old of 2022 LLM, so if we don't provide external tools, then it's knowledge is limited, if we provide, 
    # it will give recent info as well as it may search the Internet; but we changed OpenAI API to free Gemini API
    temperature=0.1, # be more deterministic/not random
    api_key=GOOGLE_API_KEY
)

# %%
# response = llm.invoke("What is the day today?")
# response

# %%
# ==============================
# PROMPT
# ==============================
# prompt is important, it loops until gives final answer -> gives an agent a predefined ReAct-style prompt: loop of T->A->O->T->A->O, etc. -> agent loop
# prompt = hub.pull("hwchase17/react") # recommended/standard tool for this task, but external prompt may be dangerous so we may write manually
prompt = """
    You are a helpful research assistant. 
    Use search for current factual information. 
    Use the weather tool for current weather. 
    Do not invent tool results.
    """


# %%
# ========================
# TOOLS
# ========================
tools = [search_tool, get_weather_data] # toolbox, the actions LLM is allowed to use

# %%
# ============================
# CREATE AGENT 
# ============================
# agent object
agent = create_agent( 
    model=llm,
    tools=tools,
    system_prompt=prompt, #all instructions
    debug=True # to see the logs of the agent invokation, what it does, what the agent is doing, debug mode, intermediate agent/tool activity
)

# %%
# ================================
# AGENT INVOCATION
# ================================
# modern invokation is message-based, agent maintains whole message memory/state
response = agent.invoke({
    "messages": [
        {
            "role": "user", # who said it? common roles: user, system, assistant, tool
            "content": "Find the capital of Switzerland and its current weather" # what did they say?
        }]})

# %%
print(response["messages"][-1].content) # the final/last message from the state of history of messages from agent execution state


