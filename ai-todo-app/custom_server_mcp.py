from fastmcp import FastMCP

mcp = FastMCP("my-custom-server")

@mcp.tool
def get_weather(city: str) -> dict:
    """
    Get the current weather for a specified city.
    Args:
        city: The name of the city.
    Returns:
        A dictionary containing the city, temperature, and condition.
    """
    # In a real app, you would call a weather API here
    weather_data = {
        "tokyo": {"temp": 68, "condition": "rainy"},
        # ... other cities
    }
    city_lower = city.lower()
    if city_lower in weather_data:
        return {"city": city, **weather_data[city_lower]}
    else:
        return {"city": city, "temp": 70, "condition": "unknown"}