from PIL import Image, ImageDraw

def create_gif():
    frames = []
    for i in range(10):
        img = Image.new('RGB', (64, 64), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((10, 20), f"Frame {i}", fill=(255, 255, 255))
        frames.append(img)
    
    frames[0].save('test_anim.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
    print("Created test_anim.gif")

if __name__ == "__main__":
    create_gif()
