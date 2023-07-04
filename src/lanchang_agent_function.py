import os
import json
import openai
import requests
from rich.console import Console
from rich import print_json
from serpapi import GoogleSearch


from langchain import LLMMathChain, OpenAI, SerpAPIWrapper, SQLDatabase, SQLDatabaseChain
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI

console = Console(highlight=False)
# GPT_MODEL = "gpt-3.5-turbo-0613"
GPT_MODEL = "gpt-4"
GoogleSearch.SERP_API_KEY = os.getenv('SERPAPI_API_KEY')
search = SerpAPIWrapper()


llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
search = SerpAPIWrapper()
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
db = SQLDatabase.from_uri("sqlite:///./Chinook.db")
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
tools = [
    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
    Tool(
        name="FooBar-DB",
        func=db_chain.run,
        description="useful for when you need to answer questions about FooBar. Input should be in the form of a question containing full context"
    )
]

agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)

def mia_print(text):
    ai_text_color = "bright_magenta"
    console.print("[b]Mia[/b]: ", end="", style=ai_text_color)
    console.print(f"\n {text}")

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

# def main():
#     # global messages
#     # mia_print("I am Mia, an AI assistant to help you find and apply jobs. \n And you can also ask me question about company benefits and working environment. \n Do you want to find a job?")
#     # messages.append({"role": "system", "content": SYSTEM_PROMPT})
#     # update_user_profile()
#     # update_job_preference()
#     # messages.append({"role": "user", "content": 'Do you want to find a job?'})
#     while True:
#         try:
#             user_input = console.input("[b]You:[/b] ").strip()
#             if user_input == 'quit' or user_input == '\q' or user_input == 'q':
#                 break
#             if user_input == 'show_messages':
#                 print_json(json.dumps(messages))
#                 continue
#             messages.append({"role": "user", "content": user_input})
#             chat_response = chat_completion_request(
#                 messages, functions=functions
#             )
#             assistant_message = chat_response.json()["choices"][0]["message"]
#             # print(chat_response.json())
#             messages.append(assistant_message)
#             function_call = assistant_message.get('function_call', None)
#             if function_call:
#                 handle_function_call(function_call)
#             else:
#                 mia_print(assistant_message['content'])
#         except KeyboardInterrupt:
#             break
# main()
