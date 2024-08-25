from PIL import Image, ImageDraw

def create_mask(image_path, coord1, coord2, output_path):
    # Open the image
    image = Image.open(image_path).convert("RGBA")

    # Create a mask the same size as the image, initially black (transparent)
    mask = Image.new("L", image.size, 0)

    # Create a drawing context on the mask
    draw = ImageDraw.Draw(mask)

    # Draw a white rectangle on the mask using the given coordinates
    draw.rectangle([coord1, coord2], fill=255)

    # Invert the mask to delete the area inside the rectangle
    inverted_mask = Image.eval(mask, lambda x: 255 - x)

    # Apply the inverted mask to the image
    masked_image = Image.composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)), inverted_mask)

    # Save the result
    masked_image.save(output_path)

# Example usage
image_path = 'baldman.png'
coord1 = (175, 50)  # First corner of the rectangle
coord2 = (475, 250)  # Opposite corner of the rectangle
output_path = 'output_image.png'

create_mask(image_path, coord1, coord2, output_path)
