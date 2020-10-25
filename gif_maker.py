import os
from PIL import Image

NEW_CASES = os.path.join(os.getcwd(), 'new_cases/')
TOTAL_CASES = os.path.join(os.getcwd(), 'total_cases/')


def create_gif(folder):
    '''Creates a new gif from all .png files in folder.'''
    im = Image.new('RGB', (700, 500))
    images = [Image.open(f'{folder}{file}')
              for file in os.listdir(folder)]

    im.save(f'{folder.lower()}.gif',
            format='GIF',
            save_all=True,
            duration=250,
            append_images=images
            )


if __name__ == '__main__':
    create_gif(NEW_CASES)
    create_gif(TOTAL_CASES)
