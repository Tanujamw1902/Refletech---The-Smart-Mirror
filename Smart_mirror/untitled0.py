import requests
 
import requests

def get_weather(api_key, latitude, longitude):
    # URL for WeatherAPI endpoint
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={latitude},{longitude}&aqi=no'
    
    # Make the API request
    response = requests.get(url)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        # Extract weather description and temperature
        weather_description = data['current']['condition']['text']
        temperature = data['current']['temp_c']
        return weather_description, temperature
    else:
        # Return error message if request fails
        return f"Error: {response.status_code} - {response.text}"

# Example usage
api_key = "3b1aa4b5268f4183a9e105831252803"  # Replace with your valid WeatherAPI key
latitude = 18.675600051879883
longitude = 73.78269958496094

# Get the weather data
result = get_weather(api_key, latitude, longitude)

# Check if result is an error message or actual weather data
if isinstance(result, tuple):
    weather_description, temperature = result
    print(f"Weather: {weather_description}, Temperature: {temperature}°C")
else:
    print(result)  # Print the error message if result is not a tuple
