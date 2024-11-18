compile: compile-bot compile-server

compile-bot:
	pyinstaller -n bot --onefile bot/main.py

compile-server:
	pyinstaller -n server --onefile server/main.py
