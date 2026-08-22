import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():

    print("========================================")
    print("MCP CLIENT")
    print("========================================")

    print(f"Connecting to: {MCP_SERVER_URL}")

    async with streamablehttp_client(
        MCP_SERVER_URL
    ) as (
        read_stream,
        write_stream,
        _,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # Initialize MCP connection
            await session.initialize()

            print("Connected to MCP server")
            print()

            # Get available tools
            tools = await session.list_tools()

            print("Available MCP tools:")
            print("----------------------------------------")

            for tool in tools.tools:
                print(f"- {tool.name}")

            print("----------------------------------------")

            print(
                f"\nTotal tools: {len(tools.tools)}"
            )


if __name__ == "__main__":
    asyncio.run(main())