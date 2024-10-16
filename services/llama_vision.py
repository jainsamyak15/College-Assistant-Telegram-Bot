import os
from together import Together
from config import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)

import os
from together import Together
from config import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)

def process_text(text):
    """
    Process text input using the Llama Vision model
    
    Args:
        text (str): The text to process
    
    Returns:
        str: Processed response from the model
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-Vision-Free",
            messages=[{"role": "user", "content": text}],
            max_tokens=5000,  # Increased max_tokens for longer responses
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=True
        )
        
        # Collect the streamed response
        full_response = ""
        for chunk in response:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
        
        if full_response:
            return full_response
        else:
            return "I apologize, but I couldn't generate a response. Could you please try rephrasing your question?"
            
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"

def process_image_and_text(prompt, text):
    """
    Process both image content and text using the Llama Vision model
    
    Args:
        prompt (str): The instruction or prompt for analyzing the text
        text (str): The extracted text to analyze
    
    Returns:
        str: Analysis result from the model
    """
    try:
        # Combine prompt and text for analysis
        combined_input = f"{prompt}\n\nText to analyze:\n{text}"
        
        response = client.chat.completions.create(
            model="meta-llama/Llama-Vision-Free",
            messages=[{"role": "user", "content": combined_input}],
            max_tokens=5000,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=True
        )
        
        # Collect the streamed response
        full_response = ""
        for chunk in response:
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
        
        if full_response:
            return full_response
        else:
            return "I apologize, but I couldn't analyze the content. Please try again."
            
    except Exception as e:
        return f"An error occurred while analyzing the content: {str(e)}"