from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

#  Base model
model = ChatGroq(model="llama-3.3-70b-versatile")

#  MCP Server config
server = {
    "flight_server": {
        "command": "python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/flight_Server.py"],
        "transport": "stdio"
    }
}

async def run():
    while True:
        client = MultiServerMCPClient(server)
        tools = await client.get_tools()

        named_tool = {tool.name: tool for tool in tools}

        #  Tool-enabled model
        tool_llm = model.bind_tools(tools)
        
        user=input("You: ")

        #  Messages
        messages = [
            SystemMessage(content="""
    You are a travel assistant.

    - Extract correct departure and arrival cities
    - NEVER merge city names
    - Call the flight tool with:
    departure, arrival, date (optional)

    After tool result:
    - DO NOT call tool again
    - Format output in human-readable way
    """),
            HumanMessage(content=user)
        ]

        #  STEP 1: LLM decides tool
        response = await tool_llm.ainvoke(messages)
        messages.append(response)

        # print("TOOL CALLS:", response.tool_calls)

        #  If no tool call
        if not response.tool_calls:
            print("No tool called")
            print(response.content)
            return

        #  STEP 2: Execute tool
        for tc in response.tool_calls:
            tool_name = tc["name"]
            raw_args = tc["args"] or {}

            #  Remove None values (VERY IMPORTANT)
            selected_args = {}
            if raw_args.get("departure"):
                selected_args["departure"] = raw_args.get("departure")
            if raw_args.get("arrival"):
                selected_args["arrival"] = raw_args.get("arrival")
            if raw_args.get("date"):
                selected_args["date"] = raw_args.get("date")

            result = await named_tool[tool_name].ainvoke(selected_args)

            # print("TOOL RESULT:", result)

            messages.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    content=json.dumps(result)   #  better than str()
                )
            )

        #  STEP 3: Final response (NO tool calling now)
        final_llm = model  # unbound model

        final_result = await final_llm.ainvoke(messages)

        print("LLM : ",final_result.content)


if __name__ == "__main__":
    asyncio.run(run())