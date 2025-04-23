 
 
import logging
import json
import os
from dotenv import load_dotenv
# Configure logging
from app.utils.logging import logger

import aisuite as ai
load_dotenv()  # Load environment variables from .env file
# Singleton pattern for AI client
class AIClientSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if AIClientSingleton._instance is None:
            AIClientSingleton._instance = ai.Client()
        return AIClientSingleton._instance

 

# Initialize conversation history
conversation_history = []

 

def get_chatgpt_response(text):
    """
    Get a response from the AI provider based on the input text and conversation history.
    Args:
        text (str): Input text to send to the AI provider
    Returns:
        str: Response from the AI provider
    """
    global conversation_history
    
    if not text:
        return "I couldn't understand what you said. Could you please repeat?"
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": text})
    
    # Prepare messages for API call with personality examples and conversation history
    messages =   conversation_history
    
    try:
        client = AIClientSingleton.get_instance()
        response = client.chat.completions.create(model="groq:llama-3.1-8b-instant", messages=messages)
        response_content = response.choices[0].message.content
        print(response_content)
        
        # Extract response text
        response_text = response_content
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Limit conversation history to last 20 exchanges to prevent token limit issues
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
            
        return response_text
    
    except Exception as e:
        logger.error(f"Error getting response from AI provider: {e}")
        return "I'm having trouble connecting to my brain right now. Can we try again in a moment?"
 

def get_user_info():
    """
    Retrieve user pruthviraj information from a text file.
    Returns:
        str: A text containing user information.
    """
    content = ""
    
    # Read user information from the file
    try:
        with open('user_info.txt', 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error("user_info.txt file not found. Please ensure the file exists.")
        return {}
    return content

def get_user_info():
    """
    Retrieve user pruthviraj resume information from a text file.
    Returns:
        str: A text containing user information.
    """
    content = ""
    
    # Read user information from the file
    try:
        with open('resume.txt', 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error("user_info.txt file not found. Please ensure the file exists.")
        return {}
    return content

def get_chatgpt_response_with_user_info(text):
    """
    Get a response from the AI provider based on the input text, conversation history, and user information.
    Args:
        text (str): Input text to send to the AI provider
    Returns:
        str: Response from the AI provider
    """
    global conversation_history
    
    user_info = get_user_info()
    if not text:
        return "I couldn't understand what you said. Could you please repeat?"
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": text})
    
    # Prepare messages for API call with personality examples, user info, and conversation history
    messages =  conversation_history
    messages.append({"role": "user", "content": f"User Info: {user_info}"})
    
    try:
        client = AIClientSingleton.get_instance()
        model = "groq:llama-3.1-8b-instant"
        
        model_name = os.getenv("MODEL_NAME") 
        response = client.chat.completions.create(model=model_name, messages=messages)
        response_content = response.choices[0].message.content
        
        # Extract response text
        response_text = response_content
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Limit conversation history to last 20 exchanges to prevent token limit issues
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
            
        return response_text
    
    except Exception as e:
        logger.error(f"Error getting response from AI provider: {e}")
        return "I'm having trouble connecting to my brain right now. Can we try again in a moment?"


def extract_data_from_txt(file_path):
    """
    Extracts data from a specified text file and returns it as a string.
    
    Args:
        file_path (str): The path to the text file to read.
        
    Returns:
        str: The content of the text file, or an error message if the file cannot be read.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        logger.error(f"{file_path} file not found. Please ensure the file exists.")
        return f"Error: {file_path} not found."
    
def get_user_info():
    """
    Retrieves user information from a text file and returns it.
    
    Returns:
        str: User information extracted from user_info.txt.
    """
    return extract_data_from_txt('user_info.txt')

def get_resume_info():
    """
    Retrieves resume information from a text file and returns it.
    
    Returns:
        str: Resume information extracted from resume.txt.
    """
    return extract_data_from_txt('resume.txt')

def get_user_info_tool() -> str:
    """Tool to retrieve user personal information. about my hoobies,opinions,belief , ambitions , goals, life story, co workers

    Returns:
        str: User personal information extracted from user_info.txt.
    """
    return get_user_info()

def get_resume_info_tool() -> str:
    """Tool to retrieve resume information. including technologies worked with , companies worked with , projects i have done , stats and achievements

    Returns:
        str: Resume information extracted from resume.txt.
    """
    return get_resume_info()
 
# Example of calling the AI with tools
def call_ai_with_tools(query):
    global conversation_history

    # User input message
    messages = [{"role": "user", "content": query}]

    # Define tools correctly (PASS ACTUAL FUNCTION REFERENCES)
    tools = [get_user_info_tool, get_resume_info_tool]  # ✅ Functions, not dicts

    # Get AI instance
    ai_instance = AIClientSingleton.get_instance()


    load_dotenv()  # Load environment variables from .env file
 
    model_name = os.getenv("MODEL_NAME")  # Read the model name from the .env file
    if not model_name :
        logger.error("Model name is empty or None. Please check the environment variable.")
        print("Error: Model name is empty or None.")
    # Make API call with tools
    response = ai_instance.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,   
        tool_choice="auto",  # Let AI choose which tool to use
        max_turns=2
    )
    # 🔹 Fix: Extract AI response properly
    response_text = None

    # Check if AI called a tool
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]  # Get first tool call
        tool_name = tool_call.function.name  # Extract function name
        tool_args = tool_call.function.arguments  # Extract arguments
        try:
            tool_args_dict = json.loads(tool_args)  # ✅ Convert JSON string to dict
        except json.JSONDecodeError:
            tool_args_dict = {}  # Handle invalid JSON
        # Call the tool function with unpacked arguments
        if tool_name == "get_user_info_tool":
            response_text = get_user_info_tool(**tool_args_dict)
        elif tool_name == "get_resume_info_tool":
            response_text = get_resume_info_tool(**tool_args_dict)
        else:
            response_text = "Error: Unknown tool requested."
    else:
        # If no tool was used, get AI response normally
        response_text = response.choices[0].message.content if response.choices[0].message else "No response"

    # Ensure response_text is not None
    response_text = response_text or "AI did not return a response."

    # Add to conversation history
    conversation_history.append({"role": "assistant", "content": response_text})

    # Keep only the last 20 messages
    conversation_history = conversation_history[-20:]

    return response_text