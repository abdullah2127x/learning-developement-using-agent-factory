import os

def list_screenshots(directory="images"):
    """Lists screenshot files in the specified directory."""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

def get_image_binary(filename, directory="images"):
    """Reads an image as binary bytes."""
    if "/" in filename or "\\" in filename:
        raise ValueError("Security: Directory traversal detected.")
    
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image '{filename}' not found.")
        
    with open(path, "rb") as f:
        return f.read()
