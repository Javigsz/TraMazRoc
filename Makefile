run:
	python3 tramazroc

setup: requirements.txt
	pip install -r requirements.txt

clean: 
	rm -rf tramazroc/__pycache__
