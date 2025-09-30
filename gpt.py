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
    
    def get_marine_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get marine weather data from OpenMeteo API"""
        try:
            url = f"{self.openmeteo_marine_base_url}/marine"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period",
                "forecast_days": DEFAULT_FORECAST_DAYS,
                "timezone": DEFAULT_TIMEZONE
            }
            
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
        
        # Get forecast for next 24 hours
        forecast_24h = []
        for i in range(min(24, len(hourly["wave_height"]))):
            forecast_24h.append({
                "hour": i,
                "wave_height": hourly["wave_height"][i],
                "wave_period": hourly["wave_period"][i],
                "swell_height": hourly["swell_wave_height"][i],
                "swell_period": hourly["swell_wave_period"][i]
            })
        
        return {
            "current_conditions": current_conditions,
            "quality_score": quality_score,
            "quality_description": self._get_quality_description(quality_score),
            "forecast_24h": forecast_24h,
            "recommendations": self._get_surf_recommendations(current_conditions, quality_score)
        }
    
    def _calculate_surf_quality(self, conditions: Dict) -> float:
        """Calculate surfing quality score based on wave conditions"""
        wave_height = conditions["wave_height"]
        wave_period = conditions["wave_period"]
        swell_height = conditions["swell_height"]
        swell_period = conditions["swell_period"]
        
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

**Surf Quality:** {analysis['quality_score']:.1f}/10 - {analysis['quality_description']}

**Recommendations:**
"""
        for rec in analysis['recommendations']:
            response += f"• {rec}\n"
        
        return response
    
    def chat_with_user(self, user_input: str) -> str:
        """Chat interface using OpenAI to handle user queries"""
        try:
            # Check if user is asking about surfing conditions
            if any(keyword in user_input.lower() for keyword in ['surf', 'surfing', 'wave', 'ocean', 'beach']):
                # Extract city name from user input
                city_name = self._extract_city_name(user_input)
                if city_name:
                    return self.get_surfing_conditions(city_name)
                else:
                    return "I'd be happy to help with surfing conditions! Please specify a city name, for example: 'What are the surfing conditions in San Diego?'"
            
            # Use OpenAI for general conversation
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful surfing and weather assistant. You can provide surfing conditions for cities using weather data. Be friendly and informative."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
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