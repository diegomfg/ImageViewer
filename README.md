# Image Viewer

> This is my first project with Claude Code. No lines of code were manually written.

A lightweight image viewer for Windows built with Python and Tkinter.

## Features

- View images (JPG, JPEG, PNG, WebP, GIF)
- Zoom in/out with mouse wheel or buttons
- Fit to window / actual size views
- Convert images between formats (PNG, JPEG, WebP, GIF, BMP)

## Requirements

- Python 3.8+
- Pillow

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python image_viewer.py
```

Or open an image directly:

```bash
python image_viewer.py path/to/image.jpg
```

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed image_viewer.py
```

The executable will be in the `dist/` folder.

## License

MIT
