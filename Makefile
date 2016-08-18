install:
	python setup.py install

update:
	pandoc -f markdown -t latex -o $(basename $(INFILE)).pdf $(INFILE)

dist/QuizGen: QuizGen.spec scripts/QuizGen.py
	pyinstaller --onefile QuizGen.spec

dist: dist/QuizGen scripts/README.md
	cp ./dist/QuizGen  ../QuizGen/linux
	cp scripts/README.md ../QuizGen/
	scp ./dist/QuizGen cdclark@scatcat.fhsu.edu:./
