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
    
    def _extract_user_experience(self, text: str) -> str:
        """Extract user experience level from query"""
        text_lower = text.lower()
        
        # Beginner indicators
        beginner_terms = [
            'beginner', 'new to surf', 'learning', 'first time', 'never surf', 
            'just started', 'novice', 'inexperienced', 'safe for beginners',
            'learning to surf', 'new surfer', 'starting out'
        ]
        
        # Advanced indicators  
        advanced_terms = [
            'experienced', 'advanced', 'expert', 'professional', 'big wave',
            'charging', 'heavy water', 'overhead', 'double overhead', 'veteran',
            'years of experience', 'expert level'
        ]
        
        # Intermediate indicators
        intermediate_terms = [
            'intermediate', 'moderate', 'some experience', 'few years',
            'comfortable', 'progressing', 'getting better', 'improving'
        ]
        
        if any(term in text_lower for term in beginner_terms):
            return 'beginner'
        elif any(term in text_lower for term in advanced_terms):
            return 'advanced'
        elif any(term in text_lower for term in intermediate_terms):
            return 'intermediate'
        
        return 'intermediate'  # Default assumption
    
    def assess_safety_for_user(self, conditions: Dict, user_experience: str) -> Dict:
        """Assess safety based on conditions and user experience level"""
        wave_height = conditions.get('wave_height', 0)
        wave_period = conditions.get('wave_period', 0)
        swell_height = conditions.get('swell_height', 0)
        
        safety_assessment = {
            'safety_level': 'unknown',
            'safety_score': 0,  # 0-10, 10 being safest
            'warnings': [],
            'recommendations': [],
            'user_experience': user_experience
        }
        
        # Safety scoring based on experience level
        if user_experience == 'beginner':
            # Beginners need smaller, gentler conditions
            if wave_height <= 1.0 and wave_period >= 8:
                safety_assessment['safety_level'] = 'safe'
                safety_assessment['safety_score'] = 8
                safety_assessment['recommendations'].append('✅ Good conditions for learning!')
            elif wave_height <= 1.5 and wave_period >= 6:
                safety_assessment['safety_level'] = 'caution'
                safety_assessment['safety_score'] = 6
                safety_assessment['recommendations'].append('⚠️ Manageable but stay close to shore')
            elif wave_height > 2.0:
                safety_assessment['safety_level'] = 'dangerous'
                safety_assessment['safety_score'] = 2
                safety_assessment['warnings'].append('🚫 Waves too big for beginners - do not surf!')
            else:
                safety_assessment['safety_level'] = 'caution'
                safety_assessment['safety_score'] = 4
                safety_assessment['recommendations'].append('⚠️ Challenging conditions - consider a lesson')
                
        elif user_experience == 'intermediate':
            # Intermediate surfers can handle moderate conditions
            if 0.8 <= wave_height <= 3.0 and wave_period >= 6:
                safety_assessment['safety_level'] = 'safe'
                safety_assessment['safety_score'] = 7
                safety_assessment['recommendations'].append('✅ Good conditions for your skill level')
            elif wave_height > 4.0:
                safety_assessment['safety_level'] = 'dangerous'
                safety_assessment['safety_score'] = 3
                safety_assessment['warnings'].append('⚠️ Large waves - only if very confident')
            else:
                safety_assessment['safety_level'] = 'caution'
                safety_assessment['safety_score'] = 5
                safety_assessment['recommendations'].append('⚠️ Proceed with caution')
                
        else:  # advanced
            # Advanced surfers can handle most conditions
            if wave_height <= 6.0:
                safety_assessment['safety_level'] = 'safe'
                safety_assessment['safety_score'] = 8
                safety_assessment['recommendations'].append('✅ Suitable for experienced surfers')
            elif wave_height > 8.0:
                safety_assessment['safety_level'] = 'caution'
                safety_assessment['safety_score'] = 6
                safety_assessment['warnings'].append('⚠️ Extreme conditions - exercise caution')
            else:
                safety_assessment['safety_level'] = 'safe'
                safety_assessment['safety_score'] = 7
                safety_assessment['recommendations'].append('✅ Challenging but manageable')
        
        # Universal safety warnings
        if wave_period < 6:
            safety_assessment['warnings'].append('🌊 Short period waves - expect choppy, unpredictable conditions')
            safety_assessment['safety_score'] -= 1
            
        if wave_height > 1.5 * swell_height and swell_height > 0:
            safety_assessment['warnings'].append('💨 Significant wind chop - conditions may be messy')
            safety_assessment['safety_score'] -= 1
            
        # Ensure safety score stays in bounds
        safety_assessment['safety_score'] = max(0, min(10, safety_assessment['safety_score']))
        
        return safety_assessment
    
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
    
    def get_safety_assessment(self, city_name: str, user_query: str = "") -> str:
        """Get safety assessment for surfing conditions based on user experience"""
        # Get basic surfing conditions first
        coords = self.geocode_city(city_name)
        if not coords:
            return f"Sorry, I couldn't find the city '{city_name}'."
        
        lat, lon = coords
        weather_data = self.get_marine_weather(lat, lon)
        if not weather_data:
            return f"Sorry, I couldn't retrieve weather data for {city_name}."
        
        analysis = self.analyze_surfing_conditions(weather_data)
        if "error" in analysis:
            return f"Sorry, I couldn't analyze conditions for {city_name}."
        
        # Extract user experience and assess safety
        user_experience = self._extract_user_experience(user_query)
        safety = self.assess_safety_for_user(analysis['current_conditions'], user_experience)
        conditions = analysis['current_conditions']
        
        # Format safety-focused response
        safety_emoji = {
            'safe': '✅',
            'caution': '⚠️', 
            'dangerous': '🚫',
            'unknown': '❓'
        }
        
        response = f"🏄‍♂️ **Safety Assessment for {city_name.title()}** ({user_experience.title()} Surfer) 🏄‍♂️\n\n"
        
        response += f"**Safety Level:** {safety_emoji[safety['safety_level']]} {safety['safety_level'].title()}\n"
        response += f"**Safety Score:** {safety['safety_score']}/10\n\n"
        
        response += "**Current Conditions:**\n"
        response += f"• Wave Height: {conditions['wave_height']:.1f}m\n"
        response += f"• Wave Period: {conditions['wave_period']:.1f}s\n"
        response += f"• Swell Height: {conditions['swell_height']:.1f}m\n\n"
        
        if safety['warnings']:
            response += "**⚠️ Safety Warnings:**\n"
            for warning in safety['warnings']:
                response += f"• {warning}\n"
            response += "\n"
        
        if safety['recommendations']:
            response += "**📋 Recommendations:**\n"
            for rec in safety['recommendations']:
                response += f"• {rec}\n"
            
        # Add experience-specific safety tips
        response += "\n**💡 Safety Tips:**\n"
        if user_experience == 'beginner':
            response += "• Always surf with others or take a lesson\n"
            response += "• Stay in shallow water where you can stand\n"
            response += "• Learn to read the conditions before entering water\n"
        elif user_experience == 'intermediate':
            response += "• Check local surf reports and hazards\n"
            response += "• Know your limits and don't push beyond them\n"
            response += "• Always surf with a buddy when possible\n"
        else:  # advanced
            response += "• Assess conditions thoroughly before entering\n"
            response += "• Consider current and weather changes\n"
            response += "• Share knowledge with less experienced surfers\n"
        
        return response
    
    def compare_surfing_cities(self, city_names: List[str], start_date: str = None, end_date: str = None) -> str:
        """Compare surfing conditions across multiple cities and provide ranking"""
        if len(city_names) < 2:
            return "Please provide at least 2 cities to compare."
        
        if len(city_names) > 5:
            return "Please limit comparisons to 5 cities or fewer for better readability."
        
        city_data = []
        
        # Get data for each city
        for city_name in city_names:
            # Geocode the city
            coords = self.geocode_city(city_name)
            if not coords:
                city_data.append({
                    'city': city_name,
                    'error': f"Could not find coordinates for {city_name}",
                    'quality_score': 0,
                    'conditions': None,
                    'analysis': None
                })
                continue
            
            lat, lon = coords
            
            # Get marine weather data
            weather_data = self.get_marine_weather(lat, lon, start_date, end_date)
            if not weather_data:
                city_data.append({
                    'city': city_name,
                    'error': f"Could not retrieve weather data for {city_name}",
                    'quality_score': 0,
                    'conditions': None,
                    'analysis': None
                })
                continue
            
            # Analyze conditions
            analysis = self.analyze_surfing_conditions(weather_data)
            if "error" in analysis:
                city_data.append({
                    'city': city_name,
                    'error': f"Could not analyze conditions for {city_name}",
                    'quality_score': 0,
                    'conditions': None,
                    'analysis': None
                })
                continue
            
            # Store successful data
            city_data.append({
                'city': city_name,
                'error': None,
                'quality_score': analysis['quality_score'],
                'conditions': analysis['current_conditions'],
                'analysis': analysis,
                'quality_description': analysis['quality_description']
            })
        # Sort cities by quality score (highest first)
        valid_cities = [city for city in city_data if city['error'] is None]
        invalid_cities = [city for city in city_data if city['error'] is not None]
        print(f"\nValid cities for comparison: {[city['city'] for city in valid_cities]}")
        # Sort valid cities by quality score
        valid_cities.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Build comparison response
        date_info = ""
        if start_date:
            date_info = f" ({start_date}" + (f" to {end_date}" if end_date and end_date != start_date else "") + ")"
        
        response = f"🏄‍♂️ **Surfing Cities Comparison{date_info}** 🏄‍♂️\n\n"
        
        if valid_cities:
            response += "**🏆 Ranking (Best to Worst):**\n"
            for i, city in enumerate(valid_cities, 1):
                rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i-1, 4)]
                conditions = city['conditions']
                response += f"{rank_emoji} **{city['city'].title()}** - Score: {city['quality_score']:.1f}/10\n"
                response += f"   {city['quality_description']}\n"
                response += f"   Wave: {conditions['wave_height']:.1f}m @ {conditions['wave_period']:.1f}s\n"
                response += f"   Swell: {conditions['swell_height']:.1f}m @ {conditions['swell_period']:.1f}s\n\n"
        
        if valid_cities:
            response += "**📊 Detailed Comparison:**\n"
            response += "```\n"
            response += f"{'City':<20} {'Score':<8} {'Wave H.':<8} {'Wave P.':<8} {'Swell H.':<9} {'Swell P.':<9}\n"
            response += "-" * 70 + "\n"
            
            for city in valid_cities:
                conditions = city['conditions']
                response += f"{city['city'].title():<20} {city['quality_score']:<8.1f} {conditions['wave_height']:<8.1f} {conditions['wave_period']:<8.1f} {conditions['swell_height']:<9.1f} {conditions['swell_period']:<9.1f}\n"
            response += "```\n\n"
        
        # Add recommendations based on ranking
        if valid_cities:
            best_city = valid_cities[0]
            response += "**🎯 Recommendations:**\n"
            
            if best_city['quality_score'] >= 6:
                response += f"• **{best_city['city'].title()}** has the best conditions right now - highly recommended!\n"
            elif best_city['quality_score'] >= 4:
                response += f"• **{best_city['city'].title()}** has the best available conditions - decent for surfing\n"
            else:
                response += f"• All cities have poor conditions currently. **{best_city['city'].title()}** is the best of limited options\n"
            
            # Add safety notes for top cities
            for city in valid_cities[:2]:  # Top 2 cities
                conditions = city['conditions']
                if conditions['wave_height'] > 3:
                    response += f"• ⚠️ **{city['city'].title()}**: High waves ({conditions['wave_height']:.1f}m) - experienced surfers only\n"
                elif conditions['wave_height'] < 0.5:
                    response += f"• 📝 **{city['city'].title()}**: Very small waves ({conditions['wave_height']:.1f}m) - good for beginners\n"
        
        # Report errors for cities that couldn't be processed
        if invalid_cities:
            response += "\n**❌ Issues:**\n"
            for city in invalid_cities:
                response += f"• **{city['city'].title()}**: {city['error']}\n"
        
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
                    "name": "get_safety_assessment",
                    "description": "Get safety assessment for surfing conditions based on user experience level. Use this when users ask about safety or mention their experience level.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city to assess safety for"
                            },
                            "user_query": {
                                "type": "string",
                                "description": "The original user query to extract experience level from"
                            }
                        },
                        "required": ["city_name", "user_query"]
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
                },
                {
                    "name": "compare_surfing_cities",
                    "description": "Compare surfing conditions across multiple cities and provide a ranking. Use this when users want to compare or rank multiple surfing locations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of city names to compare (2-5 cities recommended)"
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
                        "required": ["city_names"]
                    }
                }
            ]
            
            # First API call - let ChatGPT decide what to do
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": """You are a helpful surfing and weather assistant with safety expertise. You have access to real-time marine weather data through function calls.

Function Selection Guidelines:
- Use get_safety_assessment when users ask about safety ("is it safe?", "should I go out?") or mention their experience level ("beginner", "new to surfing", "experienced")
- Use get_surfing_conditions for general surf reports and conditions
- Use get_surfing_conditions_for_date for specific date queries
- Use compare_surfing_cities when users want to compare multiple locations ("compare", "which is better", "rank these cities", "best option between")

Always prioritize safety in your responses and encourage users to surf within their abilities. Be friendly, informative, and helpful."""},
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
                    
                elif function_name == "get_safety_assessment":
                    city_name = function_args.get("city_name")
                    user_query = function_args.get("user_query", user_input)
                    function_result = self.get_safety_assessment(city_name, user_query)
                    
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
                
                elif function_name == "compare_surfing_cities":
                    city_names = function_args.get("city_names", [])
                    start_date = function_args.get("start_date")
                    end_date = function_args.get("end_date")
                    function_result = self.compare_surfing_cities(city_names, start_date, end_date)
                
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