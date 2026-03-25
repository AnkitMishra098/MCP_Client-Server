from langchain_mcp_adapters.client import MultiServerMCPClient
import json
import asyncio 

server = {
    "flight_server": {
        "command": "python",
        "args": ["C:/Users/ankit.mishra/Desktop/amedeus/flight_Server.py"],
        "transport": "stdio"
    }
}

async def main():
    client = MultiServerMCPClient(server)
    tools = await client.get_tools()
    

    tool = next(t for t in tools if t.name == "search_flight")
    

    result = await tool.ainvoke({
        "departure": "BOM",
        "arrival": "DEL"
    })

    flights = json.loads(result[0]["text"])
    for flight in flights:
        print("Flight:", flight.get("flight"))
        print("Airlines:", flight.get("airline"))
        print("Departure:", flight.get("departure_airport"))
        print("Arrival:", flight.get("arrival_airport"))
        print("status:", flight.get("status"))
        print("Date:", flight.get("date"))
        print("\n")
        
    

if __name__ == "__main__":
    asyncio.run(main())