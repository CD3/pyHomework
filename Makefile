install:
	python setup.py install

update:
	pandoc -f markdown -t latex -o $(basename $(INFILE)).pdf $(INFILE)

QuizGen: QuizGen.spec scripts/QuizGen.py
	pyinstaller --onefile scripts/QuizGen.py
