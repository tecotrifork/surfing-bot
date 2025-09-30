#!/usr/bin/env python3
"""
Flask web application for the Surfing Conditions Bot
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add the parent directory to the path to import the bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gpt import SurfingConditionsBot
except ImportError:
    print("❌ Error: Could not import SurfingConditionsBot")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialize the bot
try:
    bot = SurfingConditionsBot()
    print("✅ Bot initialized successfully!")
except Exception as e:
    print(f"❌ Bot initialization failed: {e}")
    print("Please check your config.py and API keys")
    bot = None

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        if bot is None:
            return jsonify({
                'error': 'Bot not initialized',
                'response': 'Sorry, the bot is not properly initialized. Please check the server logs.'
            }), 500
            
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from the bot
        bot_response = bot.chat_with_user(user_message)
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'Sorry, I encountered an error while processing your request. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_initialized': bot is not None
    })

@app.route('/api/test', methods=['POST'])
def test_bot():
    """Test endpoint for debugging"""
    try:
        test_message = "What are the surfing conditions in San Diego?"
        response = bot.chat_with_user(test_message)
        
        return jsonify({
            'test_message': test_message,
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🏄‍♂️ Starting Surfing Conditions Bot Web UI...")
    print("🌐 Open your browser and go to: http://localhost:8080")
    print("📱 The bot is ready to help with surfing conditions!")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
