install req :
```python -m pip install -r requirements.txt```

build icons
```cd data```
```pyrcc5 icons.qrc -o icons_rc.py```

deploy :
```chmod +x build.sh ```
```./build.sh ```

using :
```cd build/release```
```./appcraft -h example -p 25565```