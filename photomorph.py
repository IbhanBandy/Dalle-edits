import os
import streamlit as st 
import json
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageDraw
import base64
import io

load_dotenv()
client = OpenAI()

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def create_mask(image, coord1, coord2, output_path):
    image = Image.open(image).convert("RGBA")

    mask = Image.new("L", image.size, 0)

    draw = ImageDraw.Draw(mask)

    draw.rectangle([coord1, coord2], fill=255)

    inverted_mask = Image.eval(mask, lambda x: 255 - x)

    masked_image = Image.composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)), inverted_mask)

    # Save the masked image as PNG
    masked_image.save(output_path, format="PNG")

st.title("DALLE-E Image Edit")
image = st.file_uploader("Upload your image here...", type=["png", "jpg", "jpeg"])
user_prompt = st.text_area("What do you want to add to the image...")  
button = st.button("Generate")

if user_prompt and image and button:
    base64_image = encode_image(image)

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Based on the text in {user_prompt} and the attached image, generate two ordered pairs that define a rectangular mask for the attached image fitting the content described in {user_prompt}. Provide the coordinates in pixels, with the top-left corner of the image being (0, 0). Only include the two ordered pairs in your response and nothing else. Return your answer in JSON format."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    result = response.choices[0].message.content

    try:
        result_dict = json.loads(result.strip())
        value1 = tuple(result_dict['top_left'])
        value2 = tuple(result_dict['bottom_right'])
    except json.JSONDecodeError as e:
        st.write(f"JSONDecodeError: {e.msg}")
        st.write("The response might not be a valid JSON.", result)

    # Ensure image is opened as PNG
    image = Image.open(image).convert("RGBA")

    # Create a buffer to store the PNG image
    output_buffer = io.BytesIO()

    # Save the image as PNG into the buffer
    image.save(output_buffer, format="PNG")

    # Reset buffer position to the beginning
    output_buffer.seek(0)

    # Save masked image to a file
    output_path = 'output_image.png'
    create_mask(output_buffer, value1, value2, output_path)

    # Load the output image as PNG
    with open(output_path, "rb") as mask_file:
        response = client.images.edit(
            model="dall-e-2",
            image=output_buffer,
            mask=mask_file,
            prompt=user_prompt,
            n=1,
            size="1024x1024"
        )

    image_url = response.data[0].url
    st.image(image_url, caption="DALL-E generated image")
    
    os.remove(output_path)
else:
    st.write("Please enter a prompt and upload an image to continue.")
