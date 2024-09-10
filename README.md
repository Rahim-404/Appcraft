

install req :
```python -m venv env```
```source env/bin/activate```
```python -m pip install -r requirements.txt```

build icons
```cd data```
```pyrcc5 icons.qrc -o icons_rc.py```

deploy using (nuitka) :
```nuitka main.py --follow-imports --output-dir=build --show-progress --standalone --onefile --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles --output-file=appcraft```

or (pyinstaller):
```pyinstaller --onefile --windowed --strip --icon=data/icon.ico --distpath=release --name appcraft --hidden-import pyqt5 main.py```

using (default port 25565):
```appcraft --host example ```