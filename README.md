# Weather CLI Tool

This is a command-line tool that provides current weather information for a given location using the OpenWeatherMap API made using GitHub Copilot. It allows you to retrieve various weather data such as temperature, humidity, forecast, rainfall, and daylight hours.

## Prerequisites

Before using this tool, you need to have a valid API key from OpenWeatherMap. You can sign up for a free account at [https://openweathermap.org/appid](https://openweathermap.org/appid).

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/elucidator8918/CoPilot_Hackathon_Weather_CLI
   ```

2. Build the CLI via the following command:

   ```
   cd CoPilot_Hackathon_Weather_CLI/
   pip install .
   ```

## Usage

To use the weather CLI tool, follow these steps:

1. Navigate to the project directory:

   ```
   cd CoPilot_Hackathon_Weather_CLI/   
   ```

2. Run the tool with the desired command. Here are some examples:

   - Get the Manual Page of the CLI via the command:

     ```
     weather
     ```
   
   - Get the current weather for a location:

     ```
     weather current [location]
     ```

   - Get the humidity for a location:

     ```
     weather humidity [location]
     ```

   - Get the temperature for a location:

     ```
     weather temp [location] [temperature_unit]
     ```

   - Get the forecast for a location:

     ```
     weather forecast [location]
     ```

   - Get the amount of rain for the next five days:

     ```
     weather howmuchrain [location]
     ```

   - Get the daylight hours for a location:

     ```
     weather daylight [location]
     ```

   Replace `[location]` with the desired city name or city ID. For temperature, use `[temperature_unit]` as either "F" for Fahrenheit or "C" for Celsius.

3. Follow the command prompts and view the weather information displayed in the console.

## Configuration

### API Key

To store your API key for convenience, you can use the following command:

```
weather storeapi
```

You will be prompted to enter your API key, which will be stored securely.

## Additional Commands

- View the log of the last run:

  ```
  weather log
  ```

- Dump the JSON response for current weather information:

  ```
  weather dump [location]
  ```

## Support

For any issues or questions, please open an issue in the [Repo](https://github.com/elucidator8918/CoPilot_Hackathon_Weather_CLI).
