import tinify

# Image compression function
def compress_img(image):
    tinify.key = "CgCQJfMMzMrZwRlrGQXsm1qWJf0J5br6"
    try:
        image_data = image.read()
        source = tinify.Source.from_buffer(image_data)
        compressed_data = source.to_buffer()
        print("Image compressed successfully! 👍👍")
        return compressed_data
    except Exception as e:
        print(f"An error occurred during image compression: {e} 😒")
        return None

if __name__ == "__main__":
    compress_img()
