import requests

mcp_url = "http://localhost:8000/mcp"

headers = {"Accept": "application/json, text/event-stream"}

body = {
    "jsonrpc": "2.0",
    "method": "tools/list", 
    "params": {},
    "id": 1
}

response = requests.post(mcp_url, headers=headers, json=body) 

for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))
