venv: TARGET

TARGET:
	@if [ ! -d "venv" ]; then \
		virtualenv -p python3.5 venv; \
	else echo "Virtualenv Already exists"; \
	fi
