# 🏄‍♂️ Surfing Conditions Chatbot

A Python chatbot that provides real-time surfing conditions for any city by querying the OpenMeteo API and analyzing wave data.

## Features

- **Real-time Weather Data**: Fetches current marine weather conditions from OpenMeteo API
- **City Geocoding**: Automatically finds coordinates for any city worldwide
- **Surf Quality Analysis**: Calculates a 0-10 surf quality score based on wave conditions
- **Smart Recommendations**: Provides personalized surfing advice based on conditions
- **Natural Language Interface**: Uses OpenAI GPT-4 for conversational interactions
- **Comprehensive Data**: Includes wave height, period, direction, and swell information
- **🆕 Date-Specific Forecasts**: Query conditions for specific dates or date ranges
- **🆕 Safety Assessment**: Experience-level-based safety analysis (beginner/intermediate/advanced)
- **🆕 City Comparison**: Compare multiple surfing locations with skill-level-aware rankings
- **🆕 Automatic Skill Detection**: Extracts user experience from natural language queries

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

### Complete List of Possible Prompts

#### 🌊 **Basic Surfing Conditions**

- "What are the surfing conditions in San Diego?"
- "How are the waves in Malibu?"
- "Tell me about surfing conditions in Bondi Beach"
- "What's the surf like in Gold Coast right now?"
- "Current wave conditions for Ericeira"

#### 📅 **Date-Specific Queries**

- "What will the surfing conditions be like in Biarritz on October 15th?"
- "Show me surf forecast for Hossegor from October 1st to October 5th"
- "Best surfing hours on November 2nd in Santa Monica"
- "Wave forecast for next weekend in Byron Bay"
- "Conditions for December 25th in Las Palmas"

#### 🛡️ **Safety Assessment Queries**

- "Is it safe to surf in Pipeline today? I'm a beginner"
- "Should I go out surfing in Nazaré? I'm experienced"
- "Safety assessment for Santa Cruz - I'm learning to surf"
- "Is Mavericks safe for an intermediate surfer?"
- "Can a beginner surf in Waikiki today?"

#### 🏆 **City Comparison & Ranking**

- "Compare surfing conditions between San Diego, Malibu, and Santa Monica"
- "Which is better for surfing: Biarritz, Hossegor, or San Sebastian?"
- "Rank these cities for a beginner: Gold Coast, Byron Bay, Bondi Beach"
- "What's the best surfing option between Ericeira, Peniche, and Nazaré?"
- "Compare Tenerife, Gran Canaria, and Lanzarote for intermediate surfers"

#### 🎯 **Skill-Level Specific Comparisons**

- "I'm a beginner, compare San Diego and Malibu"
- "Which city is better for advanced surfers: Pipeline or Mavericks?"
- "Rank these for intermediate level: Mundaka, Zarautz, San Sebastian"
- "Best option for a new surfer between Santa Monica and Venice Beach?"
- "Compare these spots for experienced surfers: Jeffreys Bay, Supertubes, J-Bay"

#### 🔍 **Technical Data Queries**

- "What are the coordinates for Jeffreys Bay?"
- "Show me raw marine data for coordinates 33.7701, -118.1937"
- "Wave height and period data for Malibu"
- "Detailed swell information for Portugal's coast"

#### 💬 **Conversational Interactions**

- "Tell me about the best surfing spots in California"
- "What makes a good surfing wave?"
- "Explain wave periods and why they matter"
- "What should I know about surfing safety?"
- "How do you calculate surf quality?"
- "What's the difference between wave height and swell height?"

#### 🌍 **International Locations**

- "Surfing conditions in Tavarua, Fiji"
- "How are the waves in Jeffreys Bay, South Africa?"
- "Surf report for Raglan, New Zealand"
- "Conditions in Uluwatu, Bali"
- "Wave forecast for Chicama, Peru"

#### ⚠️ **Safety-Focused Questions**

- "Are the waves too big for a beginner in Sunset Beach?"
- "Is it dangerous to surf in 4-meter waves as an intermediate?"
- "What wave height is safe for someone learning?"
- "Should experienced surfers avoid 8+ meter waves?"
- "Safety tips for surfing in powerful waves"

#### 🕐 **Time-Specific Requests**

- "Best time to surf tomorrow in Huntington Beach"
- "What time should I go surfing in Malibu this afternoon?"
- "Peak surfing hours for next Tuesday in Santa Cruz"
- "When will conditions be best this week in San Diego?"

#### 📊 **Comparison Examples by Experience Level**

- **Beginner**: "New to surfing, compare Waikiki, Cowell Beach, and Mondos"
- **Intermediate**: "Few years experience, rank Steamer Lane, Mavericks, and Ocean Beach"
- **Advanced**: "Experienced surfer, compare Pipeline, Teahupoo, and Cloudbreak"

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
   - Date-range specific forecasts
3. **Surf Quality Analysis**: Calculates a quality score based on:
   - Optimal wave height (1-3 meters)
   - Wave period (8-15 seconds ideal)
   - Swell conditions
4. **Safety Assessment**: Evaluates conditions based on user experience:
   - **Beginner**: Prioritizes waves ≤1.5m with gentle conditions
   - **Intermediate**: Suitable for waves up to 3-4m
   - **Advanced**: Can handle larger waves up to 6-8m
5. **Skill-Level Comparison**: Ranks multiple cities based on:
   - User experience level detection
   - Safety-adjusted scoring
   - Personalized recommendations
6. **Smart Recommendations**: Provides advice based on conditions and skill level

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
