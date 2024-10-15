import os
import base64
from together import Together
from config import TOGETHER_API_KEY

client = Together(api_key=TOGETHER_API_KEY)

def process_image(image_data):
    try:
        # Convert image_data to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        response = client.images.generate(
            prompt="Analyze and describe this image",
            model="black-forest-labs/FLUX.1-schnell-Free",
            width=1024,
            height=768,
            steps=4,
            n=1,
            response_format="b64_json"
        )
        image_description = base64.b64decode(response.data[0].b64_json).decode('utf-8')
        return f"Image analysis: {image_description}"
    except Exception as e:
        return f"An error occurred while processing the image: {str(e)}"