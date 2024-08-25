import os

import json
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageDraw
import base64
load_dotenv()

client = OpenAI()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def create_mask(image_path, coord1, coord2, output_path):
    image = Image.open(image_path).convert("RGBA")

    mask = Image.new("L", image.size, 0)

    draw = ImageDraw.Draw(mask)

    draw.rectangle([coord1, coord2], fill=255)

    inverted_mask = Image.eval(mask, lambda x: 255 - x)

    masked_image = Image.composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)), inverted_mask)

    masked_image.save(output_path)

user_prompt = input("Enter text here: ")  
image = input("Upload your image path here: ")

base64_image = encode_image(image)

response = client.chat.completions.create(
  model="gpt-4o",
  temperature=0.0,
  response_format={ "type": "json_object" },
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
    print(f"JSONDecodeError: {e.msg}")
    print("The response might not be a valid JSON.", result)

output_path = 'output_image.png'

create_mask(image, value1, value2, output_path)

response = client.images.edit(
  model="dall-e-2",
  image=open(image, "rb"),
  mask=open("output_image.png", "rb"),
  prompt=user_prompt,
  n=1,
  size="1024x1024"
)
image_url = response.data[0].url
print(image_url)


os.remove(output_path)