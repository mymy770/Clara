.PHONY: run stop logs

run:
	./clara.sh

stop:
	pkill -f "uvicorn" || true
	pkill -f "vite" || true
	pkill -f "clara.sh" || true

logs:
	tail -f logs/launcher/*.log

