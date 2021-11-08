import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Project Root

TEXTURES_PATH = os.path.join(ROOT_DIR, "textures\\")  # Textures path

RESULTS_PATH = os.path.join(ROOT_DIR, "results\\")  # Output images path

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
