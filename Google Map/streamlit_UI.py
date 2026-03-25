import streamlit as st
import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq

load_dotenv()

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="Travel Agent", layout="wide")
st.title("✈️ TRAVEL AGENT")
st.write("Ask about flights or hotels, and I will help you!")

# ---------------- MCP Server ----------------
server = {
    "google_map": {
        "command": "python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/Google Map/google_map_server.py"],
        "transport": "stdio"
    },
    "flight_server": {
        "command": "python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/Flight Booking/flight_Server.py"],
        "transport": "stdio"
    }
}

# ---------------- LLM ----------------
llm = ChatGroq(model='llama-3.3-70b-versatile')

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- Display Old Messages ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- Async Function to Process User Input ----------------
async def process_query(user_input):
    client = MultiServerMCPClient(server)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)

    message = [
        SystemMessage(content="""You are a travel assistant.
- Extract correct Hotel and Cities
- NEVER merge city names
- Call the search_hotels tool with: city, max_budget (optional)
- After tool result: DO NOT call tool again
- Format output in human-readable way
- For flights: extract departure, arrival, date(optional)
- If greeting, respond politely"""),
        HumanMessage(content=user_input)
    ]

    response = await llm_with_tools.ainvoke(message)
    message.append(response)

    # If no tools called
    if not response.tool_calls:
        return response.content

    # Execute tools
    for tc in response.tool_calls:
        selected_tool = tc["name"]
        selected_args = tc["args"]
        selected_id = tc["id"]

        result = await named_tools[selected_tool].ainvoke(selected_args)
        tool_msg = ToolMessage(tool_call_id=selected_id, content=json.dumps(result))
        message.append(tool_msg)

    # Final LLM response
    final_result = await llm.ainvoke(message)
    return final_result.content

# ---------------- User Input ----------------
user_input = st.text_input("Enter your query...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤖"):
            response = asyncio.new_event_loop().run_until_complete(process_query(user_input))
            st.write(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.input_box = ""