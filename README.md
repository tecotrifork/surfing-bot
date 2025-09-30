# 🏄‍♂️ Surfing Conditions Chatbot

A Python chatbot that provides real-time surfing conditions for any city by querying the OpenMeteo API and analyzing wave data.

## Features

- **Real-time Weather Data**: Fetches current marine weather conditions from OpenMeteo API
- **City Geocoding**: Automatically finds coordinates for any city worldwide
- **Surf Quality Analysis**: Calculates a 0-10 surf quality score based on wave conditions
- **Smart Recommendations**: Provides personalized surfing advice based on conditions
- **Natural Language Interface**: Uses OpenAI GPT-4 for conversational interactions
- **Comprehensive Data**: Includes wave height, period, direction, and swell information

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your configuration file:

```bash
# Copy the template configuration file
cp config.py.template config.py

# Edit config.py and add your OpenAI API key
# Get your API key from: https://platform.openai.com/api-keys
```

3. (Optional) Set your OpenAI API key as an environment variable (overrides config.py):

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Interactive Chat Mode

Run the main script to start an interactive chat session:

```bash
python gpt.py
```

Example interactions:

- "What are the surfing conditions in San Diego?"
- "How are the waves in Malibu?"
- "Tell me about surfing conditions in Bondi Beach"

### Programmatic Usage

```python
from gpt import SurfingConditionsBot

bot = SurfingConditionsBot()

# Get surfing conditions for a specific city
conditions = bot.get_surfing_conditions("San Diego")
print(conditions)

# Chat with the bot
response = bot.chat_with_user("What are the surfing conditions in Santa Monica?")
print(response)
```

### Example Script

Run the example script to see various queries in action:

```bash
python example_usage.py
```

## How It Works

1. **City Geocoding**: Uses OpenMeteo's geocoding API to convert city names to coordinates
2. **Weather Data Fetching**: Retrieves marine weather data including:
   - Wave height and direction
   - Wave period
   - Swell height, direction, and period
3. **Surf Quality Analysis**: Calculates a quality score based on:
   - Optimal wave height (1-3 meters)
   - Wave period (8-15 seconds ideal)
   - Swell conditions
4. **Smart Recommendations**: Provides advice based on conditions and skill level

## Surf Quality Scoring

The bot uses a sophisticated scoring system (0-10) based on:

- **Wave Height**: 1-3m is optimal for most surfers
- **Wave Period**: 8-15 seconds provides the best ride quality
- **Swell Height**: 1-2.5m creates good surfable waves
- **Swell Period**: 10-16 seconds indicates clean, organized swell

## API Endpoints Used

- **OpenMeteo Geocoding API**: For city-to-coordinates conversion
- **OpenMeteo Marine API**: For wave and swell data
- **OpenAI GPT-4**: For natural language processing and conversation

## Example Output

```
🏄‍♂️ **Surfing Conditions for San Diego** 🏄‍♂️

**Current Conditions:**
• Wave Height: 2.1m
• Wave Period: 12.3s
• Swell Height: 1.8m
• Swell Period: 14.2s
• Wave Direction: 245°

**Surf Quality:** 7.5/10 - Good surfing conditions! 🌊

**Recommendations:**
• Great day for surfing! Consider going out.
• Good conditions for intermediate to advanced surfers.
```

## Configuration Files

- **`config.py`**: Contains your actual API keys and settings (not committed to git)
- **`config.py.template`**: Template file showing what configuration is needed
- **`.gitignore`**: Ensures `config.py` is not committed to version control

The `config.py` file contains:

- OpenAI API key
- OpenMeteo API endpoints
- Default forecast settings

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for API calls

## License

This project is open source and available under the MIT License.
