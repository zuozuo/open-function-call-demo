import os
import re
import json
import openai
import requests
from rich.console import Console
from rich import print_json
from serpapi import GoogleSearch


from langchain import PromptTemplate
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.tools import StructuredTool, tool

from prompts import SYSTEM_PROMPT, AGENT_SYSTEM_PROMPT

def ask_for_location():
    response = agent.run('do you know which city the user want to work in?')
    regex = r"I don\'t know"
    match = re.search(regex, response)
    if match:
        # mia_print(response)
        # mia_print('Which city do you want to work in?')
        return None
    else:
        import ipdb; ipdb.set_trace(context=5)
        mia_print('get city')
        return 'Chicago'

@tool("job_search", return_direct=True)
def job_search(query: str) -> str:
    """useful for when you need to recommend some jobs to the user, or the user ask you to help find some jobs, or the user want a job"""
    import ipdb; ipdb.set_trace(context=5)
    location = ask_for_location()
    if not location:
        return 'Which city do you want to work in?'
    return 'job_search called'

@tool("job_apply", return_direct=True)
def job_apply(query: str) -> str:
    """useful for when you need to help the user to apply a job"""
    return 'job_apply called'

def init_agent():
    agent_kwargs = {
        "system_message": SystemMessage(content=SYSTEM_PROMPT)
    }

    search = SerpAPIWrapper()
    tools = [job_search, job_apply]
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

    agent = initialize_agent(
        tools,
        llm,
        verbose=True,
        memory=memory,
        agent_kwargs=agent_kwargs,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION
    )
    prompt = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)
    agent.agent.llm_chain.prompt = prompt
    return agent

def mia_print(text):
    ai_text_color = "bright_magenta"
    console.print("[b]Mia[/b]: ", end="", style=ai_text_color)
    console.print(f"\n {text}")

agent = init_agent()
console = Console(highlight=False)

def main():
    while True:
        try:
            user_input = console.input("[b]You:[/b] ").strip()
            if user_input == 'quit' or user_input == '\q' or user_input == 'q':
                break
            if user_input == 'show_messages':
                print_json(json.dumps(messages))
                continue
            response = agent.run(input=user_input)
            mia_print(response)
        except KeyboardInterrupt:
            break
main()
