compile: compile-bot compile-server

compile-bot:
	pyinstaller -n bot --onefile bot/main.py
	cp dist/bot deploy/bluetooth

compile-server:
	pyinstaller -n server --onefile server/main.py
