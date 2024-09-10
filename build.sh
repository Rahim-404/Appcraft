#!/bin/bash
nuitka main.py --follow-imports --output-dir=build --show-progress --standalone --onefile --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles --output-file=appcraft