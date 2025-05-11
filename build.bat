rm -rf build
rm -rf dist
pyinstaller.exe --paths=./Tetris Tetris/main.py -n Tetris -y -F
