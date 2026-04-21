from dataclasses import dataclass, field
from contextlib import AsyncExitStack 
import json
from pydantic import AnyUrl

from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession, types 

@dataclass
class MCPClient:
    """A clean, layered MCP Client."""
    _server_url: str
    _exit_stack: AsyncExitStack = field(default_factory=AsyncExitStack)
    _session: ClientSession | None = None

    async def __aenter__(self):
        streamable_transport = await self._exit_stack.enter_async_context(
            streamable_http_client(self._server_url)
        )  
        _read, _write, _ = streamable_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_read, _write)
        )
        await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit_stack.aclose()
        self._session = None

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Client session not initialized.")
        return self._session

    # --- HIGH LEVEL DATA METHODS ---

    async def list_tools(self):
        result = await self.session.list_tools()
        return result.tools
    
    async def call_tool(self, tool_name: str, tool_input: dict):
        return await self.session.call_tool(tool_name, tool_input)
    
    async def list_resources(self):
        result = await self.session.list_resources()
        return result.resources

    async def read_resource(self, uri: str):
        """Reads and automatically parses resource content."""
        result = await self.session.read_resource(AnyUrl(uri))
        if not result.contents:
            return None
            
        resource = result.contents[0]
        
        # Handle Text Resources
        if isinstance(resource, types.TextResourceContents):
            try:
                return json.loads(resource.text)
            except json.JSONDecodeError:
                return resource.text
        
        # Handle Binary/Blob Resources (like Images)
        return resource

async def main():
    """Example usage of the refactored client."""
    SERVER_URL = "http://localhost:8000/mcp"
    
    async with MCPClient(SERVER_URL) as client:
        print("\n--- Listing Resources ---")
        resources = await client.list_resources()
        for res in resources:
            print(f"[{res.name}] URI: {res.uri}")

        print("\n--- Reading Workspace Files ---")
        # Reading a text file
        content = await client.read_resource("file://workspace/server.py")
        print(f"Content length: {len(content) if content else 0} chars")

        print("\n--- Reading Binary Images ---")
        # Reading an image list
        images = await client.read_resource("images://screenshots/list")
        print(f"Available images: {images}")
        
        if images:
            # Read first image as binary
            img_uri = f"images://screenshots/{images[0]}"
            print(f"Reading image from URI: {img_uri}")
            binary_data = await client.read_resource("images://screenshots/Screenshot1.png")
            print(f"Read image '{images[0]}' successfully ({len(binary_data.blob) if hasattr(binary_data, 'blob') else 'unknown'} bytes)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
