import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


response = client.images.edit(
  model="dall-e-2",
  image=open("baldman.png", "rb"),
  mask=open("output_image.png", "rb"),
  prompt="Add a hat to this man's head",
  n=1,
  size="1024x1024"
)
image_url = response.data[0].url
print(image_url)