# pyinstall.py

import PyInstaller.__main__

PyInstaller.__main__.run([
    'smartlab.py',
    '--windowed',
    '--noconsole',
])
