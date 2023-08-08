run:
	python3 server.py
install:
	pip3 install -r requirements.txt
	pip3 install -e .
	cd benchmarking; pip3 install -e .
print_state:
	python print_server_state.py 
freeze:
	pip3 freeze > requirements.txt