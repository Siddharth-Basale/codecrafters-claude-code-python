import argparse
import os
import sys
from .tools import TOOLS, run_read_tool, run_write_tool
from openai import OpenAI
import json

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")
TOOL_MAP = {
    "Read": run_read_tool,
    "Write": run_write_tool
}

def callai(lst):
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=lst,
            tools=TOOLS
        )
    return chat



def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()
    print(f"args :{args.p}", file=sys.stderr)

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    messageslst = [{"role": "user", "content": args.p}]


    while True:
        chat = callai(messageslst)
        assistant_message = chat.choices[0].message
        messageslst.append(assistant_message)
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
              name = tool_call.function.name
              arg = json.loads(tool_call.function.arguments)
              if name in TOOL_MAP:
                  result = TOOL_MAP[name](**arg)
                  messageslst.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
         print(assistant_message.content)
         break

if __name__ == "__main__":
    main()
