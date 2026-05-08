import asyncio
from fastmcp import Client
from datetime import datetime

client = Client("http://localhost:8000/mcp")

async def call_tool(title: str, assignee: str, due: datetime, description: str):
    async with client:
        result = await client.list_tools_mcp()
        # result = await client.call_tool("create_task",
        #                                 {"title": title, "assignee": assignee, "due": due,
        #                                  "description": description})
        print(result)

asyncio.run(call_tool("testtask", "john", datetime.now(), "a test"))