# 🏄‍♂️ Surfing Conditions Bot - Web UI

A beautiful, modern web interface for the Surfing Conditions Bot that provides real-time surfing conditions for any location worldwide.

## ✨ Features

- **Modern Chat Interface**: Clean, responsive design with smooth animations
- **Real-time Surf Data**: Get actual wave heights, periods, and conditions
- **Smart Location Detection**: Handles cities, beaches, surf spots, and geographical features
- **Safety Assessments**: Get personalized safety recommendations based on experience level
- **Best Time Analysis**: Find the optimal surfing hours throughout the day
- **Date-specific Queries**: Ask about conditions for specific dates
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- API keys configured in `../config.py`

### Installation

1. **Navigate to the web UI directory:**

   ```bash
   cd web_ui
   ```

2. **Install dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start the web server:**

   ```bash
   python3 app.py
   ```

   Or use the startup script:

   ```bash
   ./start.sh
   ```

4. **Open your browser:**
   Go to `http://localhost:5000`

## 🎨 UI Features

### Chat Interface

- **Gradient Design**: Beautiful blue-purple gradient theme
- **Message Bubbles**: Distinct styling for user and bot messages
- **Loading Animation**: Smooth loading indicators with dots
- **Auto-scroll**: Automatically scrolls to new messages

### Example Queries

Click on any example to quickly try different types of queries:

- General conditions: "What are the surfing conditions in San Diego?"
- Famous spots: "How is the surf at Pipeline?"
- Safety questions: "Is it safe to surf at Jaws for beginners?"
- Date-specific: "Best time to surf in Malibu tomorrow"

### Responsive Design

- **Desktop**: Full-width chat interface with sidebar
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Compact design with touch-friendly buttons

## 🔧 API Endpoints

### `/api/chat` (POST)

Send a message to the bot and get a response.

**Request:**

```json
{
  "message": "What are the surfing conditions in Malibu?"
}
```

**Response:**

```json
{
  "response": "🏄‍♂️ **Surfing Conditions for Malibu** 🏄‍♂️\n\n**Current Conditions:**\n• Wave Height: 2.3m\n• Wave Period: 12.5s\n...",
  "status": "success"
}
```

### `/api/health` (GET)

Check if the bot is running properly.

### `/api/test` (POST)

Test endpoint for debugging bot functionality.

## 🎯 Example Queries

Try these example queries to see what the bot can do:

### General Conditions

- "What are the surfing conditions in San Diego?"
- "How is the surf at Bondi Beach?"
- "Surfing conditions for Uluwatu"

### Famous Surf Spots

- "What's the surf like at Pipeline?"
- "Conditions at Jaws today"
- "How is Mavericks looking?"

### Safety & Experience

- "Is it safe to surf at Jaws for beginners?"
- "Should I go out at Pipeline as an intermediate surfer?"
- "What's the surf like for experienced surfers at Teahupo'o?"

### Date-specific

- "Best time to surf in Malibu tomorrow"
- "What are the conditions at Pipeline on October 15th?"
- "Surfing conditions for Bondi Beach this weekend"

### Regional Queries

- "Best surf spots in California"
- "Surfing conditions in Hawaii"
- "What's the surf like in Australia?"

## 🛠️ Development

### Project Structure

```
web_ui/
├── index.html          # Main HTML file with React app
├── app.py             # Flask backend server
├── requirements.txt   # Python dependencies
├── start.sh          # Startup script
└── README.md         # This file
```

### Customization

#### Styling

The UI uses CSS-in-HTML with custom properties. Main colors:

- Primary: `#667eea` (blue)
- Secondary: `#764ba2` (purple)
- Background: Gradient from blue to purple

#### Adding Features

1. **New API endpoints**: Add routes in `app.py`
2. **UI components**: Modify the React components in `index.html`
3. **Styling**: Update the CSS in the `<style>` section

### Debugging

1. **Check bot initialization:**

   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Test bot functionality:**

   ```bash
   curl -X POST http://localhost:5000/api/test
   ```

3. **View server logs:**
   The Flask app runs in debug mode and shows detailed logs.

## 🌊 Supported Locations

The bot can handle:

- **Cities**: San Diego, Sydney, Barcelona, etc.
- **Famous Surf Spots**: Pipeline, Jaws, Mavericks, etc.
- **Beaches**: Bondi Beach, Venice Beach, etc.
- **Regions**: California, Hawaii, Australia, etc.
- **Geographical Features**: Bays, points, reefs, etc.

## 🔒 Security Notes

- The web UI is designed for local development
- For production deployment, consider:
  - Using HTTPS
  - Adding authentication
  - Rate limiting
  - Input validation
  - CORS configuration

## 📱 Mobile Experience

The UI is fully responsive and optimized for mobile devices:

- Touch-friendly buttons and inputs
- Optimized message layout
- Smooth scrolling
- Fast loading times

## 🎨 Design Philosophy

The UI follows modern design principles:

- **Clean & Minimal**: Focus on content, not clutter
- **Surf-themed**: Ocean-inspired colors and gradients
- **User-friendly**: Intuitive chat interface
- **Accessible**: Good contrast and readable fonts
- **Fast**: Optimized for quick interactions

Enjoy surfing the web with your new Surfing Conditions Bot! 🏄‍♂️🌊
