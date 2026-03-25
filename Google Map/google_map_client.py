from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
import asyncio 
from langchain_groq import ChatGroq
from dotenv import load_dotenv 
import json
load_dotenv() 

server={
    "google_map":{
        "command":"python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/Google Map/google_map_server.py"],
        "transport":"stdio"
    },
        "flight_server": {
        "command": "python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/Flight Booking/flight_Server.py"],
        "transport": "stdio"
    }

}

llm=ChatGroq(model='llama-3.3-70b-versatile')
# init → load tools → bind LLM → get response → execute tools → final answer


async def run():
    
    client=MultiServerMCPClient(server)

    tools=await client.get_tools()

    named_tools={}

    for tool in tools:
        print("tool using: ",tool.name)
        named_tools[tool.name]=tool

    llm_with_tools=llm.bind_tools(tools)

    while True:
        user=input("You: ")
        if user in ["Exit","exit"]:
            break 
        message=[
        SystemMessage(content= """You are a travel assistant.
        - Extract correct Hotel and Cities
        -Gives me details in the point only not in paragraph
        - NEVER merge city names
        - Call the search_hotels tool with:
        city, max_budget (optional)

        After tool result:
        - DO NOT call tool again
        - Format output in human-readable way
        
        if tool call is for flights then
        - Extract correct departure and arrival cities
        - NEVER merge city names
        - Call the flight tool with:
        departure, arrival, date (optional)
    
        After tool result:
        - DO NOT call tool again
        - Format output in human-readable way

        if Human greet you like hii hello you have simply greet him back with a good and polite msg regarding our agent .
        """),
        HumanMessage(content=user),
        ]

        response=await llm_with_tools.ainvoke(message)
        message.append(response)

        if not response.tool_calls:
            print("LLM: ",response.content)
            continue

        for tc in  response.tool_calls:
            selected_tool=tc["name"]
            selected_args=tc["args"]
            selected_id=tc["id"]
            
            result= await named_tools[selected_tool].ainvoke(selected_args)
            # print(result)
    
            tool_msg=ToolMessage(tool_call_id=selected_id,content=json.dumps(result))
            message.append(tool_msg)
        

        final_result=await llm.ainvoke(message)
        print(f"Bot :", final_result.content)
        print("\n" + "="*50 + "\n")

        
    
if __name__=="__main__":
    asyncio.run(run())