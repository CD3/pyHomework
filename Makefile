install:
	python setup.py install

update:
	pandoc -f markdown -t latex -o $(basename $(INFILE)).pdf $(INFILE)

dist/QuizGen: QuizGen.spec scripts/QuizGen.py
	pyinstaller --onefile QuizGen.spec

get_resources:
	cp $(shell pip show pint | grep Location | sed "s/Location\s*:\s*//")/pint/default_en.txt resources/
	cp $(shell pip show pint | grep Location | sed "s/Location\s*:\s*//")/pint/constants_en.txt resources/

dist: dist/QuizGen get_resources scripts/README.md
	cp ./dist/QuizGen  ../QuizGen/linux
	cp scripts/README.md ../QuizGen/
