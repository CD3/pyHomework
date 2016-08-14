install:
	python setup.py install

update:
	pandoc -f markdown -t latex -o $(basename $(INFILE)).pdf $(INFILE)

QuizGen: QuizGen.spec scripts/QuizGen.py
	pyinstaller --onefile -y --clean QuizGen.spec
