
1) We have tested our code on "lab1-19" system.

2) Please follow the following steps to run the code:

	- Navigate to the virtualenv using:
		/home/u1265867/Documents/nlp_final_project

	- Activate the virtualenv using:
		source env/bin/activate.csh

	- Go to the code folder using:
		cd nlp-project2019/code/

	- Run the code using:
		python coref.py inputCade.txt output_responses
		
		where,
				inputCade.txt --> the path of the input list file
				output_responses --> the path of the output directory
	
	- Then transfer the output responses to scoring-program/responses
	
	- Run the following command to get the scores:
		python3 scorer.py keys/ responses/ all.txt -v

3) For processing one file, our code approximately takes 2 minutes.

4) Ambuj Arora - worked on the following files:
	- semantics_by_spaCy_NP.py
	- string_matching_by_spaCy_NP.py
	- word_embeddings_by_spaCy_NP.py
	- string_matching_by_py.word
	- coref.ipynb
	- coref.py
	- reader.py

Barrett Nield- worked on the following files:
	- coref.py
	- reader.py
	- coref.ipynb
	- hobbs.py

Barrett was responsible for handling the pronouns. He implemented the Hobbs algorithm with a tweak of our own. 
Ambuj was responsible for implementing string matching by word, string matching for noun phrases(spacy) and implementing semantic similarity in noun phrases.

5) References:
	- https://www.aclweb.org/anthology/W98-1119.pdf	
	- https://github.com/nltk/nltk/wiki
	- https://spacy.io/

6) No known problems!
		
