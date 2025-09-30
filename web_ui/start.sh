#!/bin/bash

echo "🏄‍♂️ Starting Surfing Conditions Bot Web UI..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the web_ui directory."
    exit 1
fi

# Check if config.py exists in parent directory
if [ ! -f "../config.py" ]; then
    echo "❌ Error: config.py not found in parent directory."
    echo "📝 Please make sure you have set up your API keys in config.py"
    exit 1
fi

# Install requirements if needed
echo "📦 Installing requirements..."
pip3 install -r requirements.txt

echo ""
echo "🚀 Starting the web server..."
echo "🌐 Open your browser and go to: http://localhost:5000"
echo "📱 The bot is ready to help with surfing conditions!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python3 app.py
