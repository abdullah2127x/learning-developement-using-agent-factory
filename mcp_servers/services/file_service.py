import os

def list_workspace_files(directory="."):
    """Lists non-hidden files in the specified directory."""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith(".")]

def read_file_content(filename, directory="."):
    """Safely reads a file's content, preventing directory traversal."""
    if "/" in filename or "\\" in filename:
        raise ValueError("Security: Directory traversal detected.")
    
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{filename}' not found.")
        
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
