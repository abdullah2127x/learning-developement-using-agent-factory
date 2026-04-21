# from mcp.server.fastmcp import FastMCP
# from services import file_service, image_service
# from mcp.server.fastmcp.prompts import base
# # Initialize FastMCP server
# mcp = FastMCP(name="hello_mcp", stateless_http=True)
# # ==============================RESOURCES========================
# # --- WORKSPACE FILE RESOURCES ---

# # @mcp.resource(uri="file://workspace/list", name="list_workspace_files")
# # def list_workspace_files() -> list[str]:
# #     """Lists files in the current directory."""
# #     return file_service.list_workspace_files(".")

# # @mcp.resource(uri="file://workspace/{filename}", name="read_file")
# # def read_workspace_file(filename: str) -> str:
# #     """Reads a text file from the workspace."""
# #     try:
# #         return file_service.read_file_content(filename)
# #     except Exception as e:
# #         return f"Error: {str(e)}"

# # # --- IMAGE RESOURCES ---

# # @mcp.resource(uri="images://screenshots/list", name="list_screenshots")
# # def list_screenshots() -> list[str]:
# #     """Lists available screenshot filenames."""
# #     return image_service.list_screenshots("images")

# # @mcp.resource(uri="images://screenshots/{name}", name="get_screenshot")
# # def get_screenshot(name: str) -> bytes:
# #     """Fetches an image as binary data."""
# #     return image_service.get_image_binary(name, "images")

# # ==============================Prompts========================
# @mcp.prompt(name="greet", description="Greets the user")
# def greet(name: str) -> str:
#     """Greets the user with a message."""

#     # return f"Hello, {name}! Welcome to the MCP server."
#     return [base.UserMessage(content=base.TextContent(type="text", text=name)), base.AssistantMessage(content=base.TextContent(type="text", text="How can I assist you today?"))]
# # --- TOOLS ---

# @mcp.tool(name="search", description="searching online")
# def search_online(query: str):
#     """Searches online for the given query."""
#     return f"Searching online for: {query}"

# # Export the app
# mcp_app = mcp.streamable_http_app()







from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="hello_mcp",stateless_http=True)

mcp_app = mcp.streamable_http_app()