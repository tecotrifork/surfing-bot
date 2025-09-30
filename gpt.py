import os
import requests
import json
from openai import OpenAI
from typing import Dict, List, Optional, Tuple

# Import configuration
try:
    from config import OPENAI_API_KEY, OPENMETEO_GEO_BASE_URL, OPENMETEO_MARINE_BASE_URL, DEFAULT_FORECAST_DAYS, DEFAULT_TIMEZONE
except ImportError:
    print("❌ Error: config.py file not found!")
    print("📝 Please copy config.py.template to config.py and add your API keys")
    print("   cp config.py.template config.py")
    exit(1)

class SurfingConditionsBot:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
        )
        self.openmeteo_geo_base_url = OPENMETEO_GEO_BASE_URL
        self.openmeteo_marine_base_url = OPENMETEO_MARINE_BASE_URL

        
    def geocode_city(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a city using OpenMeteo geocoding API"""
        try:
            url = f"{self.openmeteo_geo_base_url}/search"
            params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            print(f"\n🗺️  Geocoding city: {city_name}")
            print(f"🔗 Geocoding API URL: {url}")
            print(f"📋 Geocoding Parameters: {params}")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            print(f"✅ Geocoding API Response:")
            print("=" * 30)
            print(json.dumps(data, indent=2))
            print("=" * 30)
            
            if data.get("results"):
                result = data["results"][0]
                lat, lon = result["latitude"], result["longitude"]
                print(f"📍 Found coordinates: {lat}, {lon}")
                return lat, lon
            else:
                print(f"❌ No results found for city: {city_name}")
                return None
            
        except Exception as e:
            print(f"❌ Error geocoding city {city_name}: {e}")
            return None
    
    def get_marine_weather(self, lat: float, lon: float, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """Get marine weather data from OpenMeteo API"""
        try:
            url = f"{self.openmeteo_marine_base_url}/marine"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period",
                "timezone": DEFAULT_TIMEZONE
            }
            
            # Add date parameters if provided
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            else:
                params["forecast_days"] = DEFAULT_FORECAST_DAYS
            
            print(f"\n🌊 Fetching marine weather data from OpenMeteo API...")
            print(f"📍 Coordinates: {lat}, {lon}")
            print(f"🔗 API URL: {url}")
            print(f"📋 Parameters: {params}")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            print(f"\n✅ API Response received successfully!")
            print(f"📊 Raw API Data:")
            print("=" * 50)
            print(json.dumps(data, indent=2))
            print("=" * 50)
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching marine weather: {e}")
            return None
    
    def analyze_surfing_conditions(self, weather_data: Dict) -> Dict:
        """Analyze weather data to determine surfing conditions"""
        if not weather_data or "hourly" not in weather_data:
            return {"error": "No weather data available"}
        
        hourly = weather_data["hourly"]
        
        # Get current conditions (first hour)
        current_conditions = {
            "wave_height": hourly["wave_height"][0],
            "wave_direction": hourly["wave_direction"][0],
            "wave_period": hourly["wave_period"][0],
            "swell_height": hourly["swell_wave_height"][0],
            "swell_direction": hourly["swell_wave_direction"][0],
            "swell_period": hourly["swell_wave_period"][0]
        }
        
        # Calculate surfing quality score (0-10)
        quality_score = self._calculate_surf_quality(current_conditions)
        
        # Analyze all hours to find best times
        hourly_analysis = []
        for i in range(len(hourly["wave_height"])):
            hour_conditions = {
                "hour": i,
                "time": hourly.get("time", [])[i] if hourly.get("time") else f"Hour {i}",
                "wave_height": hourly["wave_height"][i],
                "wave_direction": hourly["wave_direction"][i],
                "wave_period": hourly["wave_period"][i],
                "swell_height": hourly["swell_wave_height"][i],
                "swell_direction": hourly["swell_wave_direction"][i],
                "swell_period": hourly["swell_wave_period"][i]
            }
            hour_conditions["quality_score"] = self._calculate_surf_quality(hour_conditions)
            hourly_analysis.append(hour_conditions)
        
        # Find best surfing times (top 3 hours with highest scores)
        # Filter out entries with None quality scores and sort
        valid_hours = [hour for hour in hourly_analysis if hour["quality_score"] is not None]
        best_times = sorted(valid_hours, key=lambda x: x["quality_score"], reverse=True)[:3]
        
        # Get forecast for next 24 hours (for backward compatibility)
        forecast_24h = hourly_analysis[:min(24, len(hourly_analysis))]
        
        return {
            "current_conditions": current_conditions,
            "quality_score": quality_score,
            "quality_description": self._get_quality_description(quality_score),
            "forecast_24h": forecast_24h,
            "best_times": best_times,
            "hourly_analysis": hourly_analysis,
            "recommendations": self._get_surf_recommendations(current_conditions, quality_score)
        }
    
    def _calculate_surf_quality(self, conditions: Dict) -> float:
        """Calculate surfing quality score based on wave conditions"""
        wave_height = conditions.get("wave_height")
        wave_period = conditions.get("wave_period")
        swell_height = conditions.get("swell_height")
        swell_period = conditions.get("swell_period")
        
        # Handle None values by returning 0 score
        if wave_height is None or wave_period is None or swell_height is None or swell_period is None:
            return 0.0
        
        score = 0
        
        # Wave height scoring (optimal: 1-3 meters)
        if 1.0 <= wave_height <= 3.0:
            score += 3
        elif 0.5 <= wave_height < 1.0 or 3.0 < wave_height <= 4.0:
            score += 2
        elif wave_height < 0.5 or wave_height > 4.0:
            score += 0.5
        
        # Wave period scoring (optimal: 8-15 seconds)
        if 8 <= wave_period <= 15:
            score += 3
        elif 6 <= wave_period < 8 or 15 < wave_period <= 18:
            score += 2
        else:
            score += 1
        
        # Swell height scoring
        if 1.0 <= swell_height <= 2.5:
            score += 2
        elif 0.5 <= swell_height < 1.0 or 2.5 < swell_height <= 3.5:
            score += 1.5
        else:
            score += 0.5
        
        # Swell period scoring
        if 10 <= swell_period <= 16:
            score += 2
        elif 8 <= swell_period < 10 or 16 < swell_period <= 20:
            score += 1.5
        else:
            score += 1
        
        return min(10, max(0, score))
    
    def _get_quality_description(self, score: float) -> str:
        """Get human-readable quality description"""
        if score >= 8:
            return "Excellent surfing conditions! 🏄‍♂️"
        elif score >= 6:
            return "Good surfing conditions! 🌊"
        elif score >= 4:
            return "Fair surfing conditions ⚡"
        elif score >= 2:
            return "Poor surfing conditions 😕"
        else:
            return "Very poor surfing conditions 🚫"
    
    def _get_surf_recommendations(self, conditions: Dict, score: float) -> List[str]:
        """Get surfing recommendations based on conditions"""
        recommendations = []
        
        wave_height = conditions["wave_height"]
        wave_period = conditions["wave_period"]
        
        if score >= 6:
            recommendations.append("Great day for surfing! Consider going out.")
        elif score >= 4:
            recommendations.append("Decent conditions, but check local reports for safety.")
        else:
            recommendations.append("Not ideal for surfing today. Consider other activities.")
        
        if wave_height > 3:
            recommendations.append("⚠️ High waves - only for experienced surfers!")
        elif wave_height < 0.5:
            recommendations.append("Very small waves - might be better for beginners or longboarding.")
        
        if wave_period < 6:
            recommendations.append("Short period waves - conditions might be choppy.")
        elif wave_period > 18:
            recommendations.append("Long period swell - could be powerful, check local conditions.")
        
        return recommendations
    
    def get_surfing_conditions(self, city_name: str) -> str:
        """Main method to get surfing conditions for a city"""
        # Geocode the city
        coords = self.geocode_city(city_name)
        if not coords:
            return f"Sorry, I couldn't find the city '{city_name}'. Please check the spelling and try again."
        
        lat, lon = coords
        
        # Get marine weather data
        weather_data = self.get_marine_weather(lat, lon)
        if not weather_data:
            return f"Sorry, I couldn't retrieve weather data for {city_name}."
        
        # Analyze conditions
        analysis = self.analyze_surfing_conditions(weather_data)
        
        if "error" in analysis:
            return f"Sorry, I couldn't analyze the surfing conditions for {city_name}."
        
        # Format response
        conditions = analysis["current_conditions"]
        response = f"""
🏄‍♂️ **Surfing Conditions for {city_name.title()}** 🏄‍♂️

**Current Conditions:**
• Wave Height: {conditions['wave_height']:.1f}m
• Wave Period: {conditions['wave_period']:.1f}s
• Swell Height: {conditions['swell_height']:.1f}m
• Swell Period: {conditions['swell_period']:.1f}s
• Wave Direction: {conditions['wave_direction']:.0f}°

**Surf Quality:** {analysis['quality_score']:.2f}/10 - {analysis['quality_description']}

**Best Surfing Times:**
"""
        
        # Add best times if available
        if "best_times" in analysis and analysis["best_times"]:
            for i, best_time in enumerate(analysis["best_times"], 1):
                time_str = best_time.get("time", f"Hour {best_time['hour']}")
                response += f"{i}. {time_str} - Quality: {best_time['quality_score']:.2f}/10 (Wave: {best_time['wave_height']:.1f}m, Period: {best_time['wave_period']:.1f}s)\n"
        
        response += "\n**Recommendations:**\n"
        for rec in analysis['recommendations']:
            response += f"• {rec}\n"
        
        return response
    
    def get_surfing_conditions_for_date(self, city_name: str, start_date: str, end_date: str = None) -> str:
        """Get surfing conditions for a specific date or date range"""
        # Geocode the city
        coords = self.geocode_city(city_name)
        if not coords:
            return f"Sorry, I couldn't find the city '{city_name}'. Please check the spelling and try again."
        
        lat, lon = coords
        
        # Use end_date as start_date if only one date provided
        if not end_date:
            end_date = start_date
        
        # Get marine weather data for the specific date range
        weather_data = self.get_marine_weather(lat, lon, start_date, end_date)
        if not weather_data:
            return f"Sorry, I couldn't retrieve weather data for {city_name} on {start_date}."
        
        # Analyze conditions
        analysis = self.analyze_surfing_conditions(weather_data)
        
        if "error" in analysis:
            return f"Sorry, I couldn't analyze the surfing conditions for {city_name} on {start_date}."
        
        # Format response with date information
        conditions = analysis["current_conditions"]
        date_info = f" from {start_date} to {end_date}" if start_date != end_date else f" on {start_date}"
        
        response = f"""
🏄‍♂️ **Surfing Conditions for {city_name.title()}{date_info}** 🏄‍♂️

**Current Conditions:**
• Wave Height: {conditions['wave_height']:.1f}m
• Wave Period: {conditions['wave_period']:.1f}s
• Swell Height: {conditions['swell_height']:.1f}m
• Swell Period: {conditions['swell_period']:.1f}s
• Wave Direction: {conditions['wave_direction']:.0f}°

**Surf Quality:** {analysis['quality_score']:.2f}/10 - {analysis['quality_description']}

**Best Surfing Times:**
"""
        
        # Add best times if available
        if "best_times" in analysis and analysis["best_times"]:
            for i, best_time in enumerate(analysis["best_times"], 1):
                time_str = best_time.get("time", f"Hour {best_time['hour']}")
                response += f"{i}. {time_str} - Quality: {best_time['quality_score']:.2f}/10 (Wave: {best_time['wave_height']:.1f}m, Period: {best_time['wave_period']:.1f}s)\n"
        
        response += "\n**Recommendations:**\n"
        for rec in analysis['recommendations']:
            response += f"• {rec}\n"
        
        return response
    
    def chat_with_user(self, user_input: str) -> str:
        """Chat interface using OpenAI with function calling"""
        try:
            # Define the functions ChatGPT can call
            functions = [
                {
                    "name": "get_surfing_conditions",
                    "description": "Get current surfing conditions for a specific city including wave height, period, swell data, and quality score",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city to get surfing conditions for (e.g., 'San Diego', 'Las Palmas de Gran Canaria')"
                            }
                        },
                        "required": ["city_name"]
                    }
                },
                {
                    "name": "get_surfing_conditions_for_date",
                    "description": "Get surfing conditions for a specific date or date range. Use this when users ask about specific dates like 'October 1st 2025' or 'best surfing hour on October 1st'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city to get surfing conditions for"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (e.g., '2025-10-01')"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format (optional, defaults to start_date if not provided)"
                            }
                        },
                        "required": ["city_name", "start_date"]
                    }
                },
                {
                    "name": "geocode_city",
                    "description": "Get latitude and longitude coordinates for a city name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city to geocode"
                            }
                        },
                        "required": ["city_name"]
                    }
                },
                {
                    "name": "get_marine_weather",
                    "description": "Get raw marine weather data from OpenMeteo API for specific coordinates and optional date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate"
                            },
                            "longitude": {
                                "type": "number", 
                                "description": "Longitude coordinate"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format (optional)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format (optional)"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            ]
            
            # First API call - let ChatGPT decide what to do
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": """You are a helpful surfing and weather assistant. You have access to real-time marine weather data through function calls.

When users ask about surfing conditions in specific cities, use the get_surfing_conditions function to get the data, then present it in a friendly, conversational way.

You can also answer general questions about surfing, weather, ocean conditions, and other topics. Be friendly, informative, and helpful."""},
                    {"role": "user", "content": user_input}
                ],
                functions=functions,
                function_call="auto",
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Check if ChatGPT wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                # Execute the function
                if function_name == "get_surfing_conditions":
                    city_name = function_args.get("city_name")
                    function_result = self.get_surfing_conditions(city_name)
                    
                elif function_name == "get_surfing_conditions_for_date":
                    city_name = function_args.get("city_name")
                    start_date = function_args.get("start_date")
                    end_date = function_args.get("end_date")
                    function_result = self.get_surfing_conditions_for_date(city_name, start_date, end_date)
                    
                elif function_name == "geocode_city":
                    city_name = function_args.get("city_name")
                    coords = self.geocode_city(city_name)
                    function_result = f"Coordinates for {city_name}: {coords}" if coords else f"Could not find coordinates for {city_name}"
                    
                elif function_name == "get_marine_weather":
                    lat = function_args.get("latitude")
                    lon = function_args.get("longitude")
                    start_date = function_args.get("start_date")
                    end_date = function_args.get("end_date")
                    weather_data = self.get_marine_weather(lat, lon, start_date, end_date)
                    function_result = f"Marine weather data: {json.dumps(weather_data, indent=2)}" if weather_data else "Could not retrieve marine weather data"
                
                else:
                    function_result = "Unknown function called"
                
                # Second API call - give ChatGPT the function result
                messages = [
                    {"role": "system", "content": "You are a helpful surfing assistant. Present the function results in a friendly, conversational way."},
                    {"role": "user", "content": user_input}
                ]
                
                # Only add assistant message if there's content
                if message.content:
                    messages.append({"role": "assistant", "content": message.content})
                
                # Add the function result
                messages.append({"role": "function", "name": function_name, "content": function_result})
                
                follow_up_response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1000
                )
                
                return follow_up_response.choices[0].message.content
            
            # No function call needed, return ChatGPT's response
            return message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"
    
    def _extract_city_name(self, text: str) -> Optional[str]:
        """Extract city name from user input"""
        # Simple extraction - look for common patterns
        import re
        
        # Look for "in [city]" pattern
        match = re.search(r'in\s+([A-Za-z\s]+?)(?:\?|$|,|\.)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look for city names after common question words
        match = re.search(r'(?:what|how|tell me about|surfing conditions for|conditions in)\s+([A-Za-z\s]+?)(?:\?|$|,|\.)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None

def test_api_calls():
    """Test function to verify API calls are working"""
    bot = SurfingConditionsBot()
    
    print("🧪 Testing OpenMeteo API calls...")
    print("=" * 50)
    
    # Test with a known coastal city
    test_city = "San Diego"
    print(f"Testing with city: {test_city}")
    
    # Test geocoding
    coords = bot.geocode_city(test_city)
    if coords:
        lat, lon = coords
        print(f"\n✅ Geocoding successful: {lat}, {lon}")
        
        # Test marine weather
        weather_data = bot.get_marine_weather(lat, lon)
        if weather_data:
            print(f"\n✅ Marine weather data retrieved successfully!")
            print(f"📊 Data contains {len(weather_data.get('hourly', {}).get('time', []))} hourly data points")
        else:
            print(f"\n❌ Failed to retrieve marine weather data")
    else:
        print(f"\n❌ Failed to geocode city: {test_city}")
    
    print("\n" + "=" * 50)

def main():
    """Main function to run the chatbot"""
    bot = SurfingConditionsBot()
    
    print("🏄‍♂️ Welcome to the Surfing Conditions Chatbot! 🏄‍♂️")
    print("Ask me about surfing conditions in any city!")
    print("Type 'test' to test API calls, 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thanks for using the Surfing Conditions Chatbot! 🏄‍♂️")
            break
        elif user_input.lower() == 'test':
            test_api_calls()
        elif user_input:
            response = bot.chat_with_user(user_input)
            print(f"Bot: {response}\n")

if __name__ == "__main__":
    main()