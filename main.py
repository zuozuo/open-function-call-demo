import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from rich.console import Console

GPT_MODEL = "gpt-3.5-turbo-0613"

SYSTEM_PROMPT = '''
You are Mia - an expert assistant for helping people to find and apply a job. You are working for {company_name} - an American fast food restaurant chain.
And you can also answer questions about company benefits and working environment.

You are given the following extracted parts of a document and a question. Provide a conversational answer based on the context provided.
You should only provide hyperlinks that reference the context below. Do NOT make up hyperlinks.
If you can't find the answer in the context below, you should apologize (without mentioning the word context) and say you don't have the information. Don't try to make up an answer.
If the question is not related to the context, politely respond that you don't have access this information but this can be discussed with the hiring manager.
Always write short and concise responses and make sure to answer the specific question.
If you respond that you don't have a specific information add that this can be discussed during the interview with the hiring manager.

The most importmant conservation rule is: Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
'''

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    # print('------------------------------')
    # print(messages)
    # print('------------------------------')
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        if response.ok:
            return response
        else:
            print(response)
            print(response.json())
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    formatted_messages = []
    for message in messages:
        if message["role"] == "system":
            formatted_messages.append(f"system: {message['content']}\n")
        elif message["role"] == "user":
            formatted_messages.append(f"user: {message['content']}\n")
        elif message["role"] == "assistant" and message.get("function_call"):
            formatted_messages.append(f"assistant: {message['function_call']}\n")
        elif message["role"] == "assistant" and not message.get("function_call"):
            formatted_messages.append(f"assistant: {message['content']}\n")
        elif message["role"] == "function":
            formatted_messages.append(f"function ({message['name']}): {message['content']}\n")
    for formatted_message in formatted_messages:
        print(
            colored(
                formatted_message,
                role_to_color[messages[formatted_messages.index(formatted_message)]["role"]],
            )
        )

functions = [
    {
        "name": "recommend_jobs",
        "description": "Recommend jobs for user",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "job_title": {
                    "type": "string",
                    "description": "The title of job, or the occupation",
                },
                "is_full_time": {
                    "type": "boolean",
                    "description": "Is this job full-time or part-time",
                },
            },
            "required": ["location", "job_title"],
        },
    },
    {
        "name": "apply_job",
        "description": "Help user to apply for a specific position",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The email of the applicant",
                },
                "num_days": {
                    "type": "integer",
                    "description": "The number of days to forecast",
                }
            },
            "required": ["location", "format", "num_days"]
        },
    },
]

def handle_function_call(function_info):
    name = function_info['name']
    arguments = json.loads(function_info['arguments'])
    print(name)
    print(arguments)


def main():
    console = Console(highlight=False)
    ai_text_color = "bright_magenta"
    character = "ChatGPT"
    console.print(f"[b]{character}[/b]: ", end="", style=ai_text_color)
    console.print("I am Mia, an AI assistant to help to find and apply jobs, and you can also ask me question about company benefits and working environment?")
    messages = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})
    while True:
        try:
            user_input = console.input("[b]You:[/b] ").strip()
            if not user_input:
                break
            messages.append({"role": "user", "content": user_input})
            chat_response = chat_completion_request(
                messages, functions=functions
            )
            assistant_message = chat_response.json()["choices"][0]["message"]
            messages.append(assistant_message)
            console.print(f"[b]{character}[/b]: ", end="", style=ai_text_color)
            function_call = assistant_message.get('function_call', None)
            if function_call:
                handle_function_call(function_call)
            else:
                console.print(assistant_message)
        except KeyboardInterrupt:
            break

main()
