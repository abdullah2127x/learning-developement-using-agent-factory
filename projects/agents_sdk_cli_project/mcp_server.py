from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greet_mcp", stateless_http=True)
  

# @mcp.tool()
# async def greet(name: str) -> str:
#     return f"Hello, {name}! Welcome to the MCP server."


mcp_app = mcp.streamable_http_app()


