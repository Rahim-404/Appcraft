#!/bin/bash
mkdir build
cd  build
pyinstaller --onefile --windowed --strip --icon=icon.ico --distpath=release --name appcraft --hidden-import pyside6 ../main.py
#pyinstaller --onefile --windowed --icon=icon.ico --distpath=release --name appcraft ../main.py
