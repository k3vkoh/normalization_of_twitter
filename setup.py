import json
from nltk.corpus import words

heuristic_path = 'heuristics/'

abbrevations_path = heuristic_path + 'abbreviations.json'
emojis_path = heuristic_path + 'emojis.json'
oov_path = heuristic_path + 'oov_list.json'
paper_path = 'dataset-lexnorm2015/'

with open(abbrevations_path, 'r') as file:
	abbreviations_list = json.load(file)

with open(emojis_path, 'r') as file:
	emojis_list = json.load(file)

with open(oov_path, 'r') as file:
	oov_list = json.load(file)
	
with open(paper_path + 'train_data.json', 'r') as file:
	training_data = json.load(file)

english_words = list(set(words.words()))
abbrev = list(abbreviations_list.keys())
extended_words = english_words + [x.lower() for x in abbrev]
	
training_set = []

for x in training_data:
	temp = []
	for y in range(len(x['input'])):
		if ('@' in x['input'][y]) or ('#' in x['input'][y]) or (x['input'][y].lower() == x['output'][y].lower()):
			temp.append((x['input'][y].lower(), 'NN'))
		else:
			temp.append((x['input'][y].lower(), 'N'))
	training_set.append(temp)
	

def return_abbreviations():
	return abbreviations_list

def return_emojis():
	return emojis_list

def return_oov():
	return oov_list

def return_extended_words():
	return extended_words

def return_training_set():
	return training_set