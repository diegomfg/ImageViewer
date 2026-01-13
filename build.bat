@echo off
echo Installing dependencies...
pip install pillow pyinstaller

echo.
echo Building Image Viewer executable...
pyinstaller --onefile --windowed --name "ImageViewer" --clean image_viewer.py

echo.
echo Build complete!
echo Executable is located at: dist\ImageViewer.exe
pause
