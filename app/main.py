import argparse
import os
import sys
from .tools import TOOLS, run_read_tool
from openai import OpenAI
import json

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")
TOOL_MAP = {
    "Read": run_read_tool,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
        tools=TOOLS
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    print("Logs from your program will appear here!", file=sys.stderr)

    messages = chat.choices[0].message

    if messages.tool_calls:
        for tool_call in messages.tool_calls:
            name = tool_call.function.name
            arg = json.loads(tool_call.function.arguments)
            if name in TOOL_MAP:
                result = TOOL_MAP[name](**arg)
                print(result)
    else:
        print(chat.choices[0].message.content)



    


if __name__ == "__main__":
    main()
