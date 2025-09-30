#!/usr/bin/env python3
"""
Example usage of the Surfing Conditions Chatbot
"""

from gpt import SurfingConditionsBot

def example_queries():
    """Demonstrate various ways to query the chatbot"""
    bot = SurfingConditionsBot()
    
    # Example queries
    queries = [
        "What are the surfing conditions in San Diego?",
        "How are the waves in Malibu?",
        "Tell me about surfing conditions in Bondi Beach",
        "What's the surf like in Huntington Beach?",
        "Surfing conditions in Santa Monica",
        "How are the waves in Venice Beach?"
    ]
    
    print("🏄‍♂️ Surfing Conditions Chatbot Examples 🏄‍♂️\n")
    
    for query in queries:
        print(f"Query: {query}")
        print(f"Response: {bot.chat_with_user(query)}")
        print("-" * 50)

if __name__ == "__main__":
    example_queries()
