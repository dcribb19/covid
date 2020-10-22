import os
from PIL import Image

NEW_CASE_FILE = os.path.join(os.getcwd(), 'new_cases/')
TOTAL_CASES = os.path.join(os.getcwd(), 'total_cases/')


def new_cases_gif():
    im = Image.new('RGB', (700, 500))
    images = [Image.open(f'{NEW_CASE_FILE}{file}')
              for file in os.listdir(NEW_CASE_FILE)]

    im.save('new_cases.gif',
            format='GIF',
            save_all=True,
            duration=250,
            append_images=images
            )


def total_cases_gif():
    im = Image.new('RGB', (700, 500))
    images = [Image.open(f'{TOTAL_CASES}{file}')
              for file in os.listdir(TOTAL_CASES)]

    im.save('total_cases.gif',
            format='GIF',
            save_all=True,
            duration=250,
            append_images=images
            )


if __name__ == '__main__':
    new_cases_gif()
    total_cases_gif()
