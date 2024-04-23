import os
import pandas as pd
import numpy as np
import json
import sklearn_crfsuite
from sklearn.model_selection import train_test_split
from autocorrect import Speller
import nltk
from nltk.corpus import words

nltk.download('words')

heuristic_path = 'heuristics/'

abbrevations_path = heuristic_path + 'abbreviations.json'
emojis_path = heuristic_path + 'emojis.json'
oov_path = heuristic_path + 'oov_list.json'

with open(abbrevations_path, 'r') as file:
	abbreviations_list = json.load(file)

with open(emojis_path, 'r') as file:
	emojis_list = json.load(file)

with open(oov_path, 'r') as file:
	oov_list = json.load(file)

english_words = list(set(words.words()))

abbrev = list(abbreviations_list.keys())
extended_words = english_words + [x.lower() for x in abbrev]

paper_path = 'dataset-lexnorm2015/'
	
with open(paper_path + 'train_data.json', 'r') as file:
	training_data = json.load(file)
	
training_set = []

for x in training_data:
	temp = []
	for y in range(len(x['input'])):
		if ('@' in x['input'][y]) or ('#' in x['input'][y]) or (x['input'][y].lower() == x['output'][y].lower()):
			temp.append((x['input'][y].lower(), 'NN'))
		else:
			temp.append((x['input'][y].lower(), 'N'))
	training_set.append(temp)

# functions for crf
def word2features(sent, i):
	word = sent[i][0]

	features = {
		'bias': 1.0,
		'word.lower()': word.lower(),
		'word[-3:]': word[-3:],
		'word[-2:]': word[-2:],
		'word.isupper()': word.isupper(),
		'word.istitle()': word.istitle(),
		'word.isdigit()': word.isdigit(),
	}
	if i > 0:
		word1 = sent[i-1][0]
		features.update({
			'-1:word.lower()': word1.lower(),
			'-1:word.istitle()': word1.istitle(),
		})
	else:
		features['BOS'] = True

	if i < len(sent)-1:
		word1 = sent[i+1][0]
		features.update({
			'+1:word.lower()': word1.lower(),
			'+1:word.istitle()': word1.istitle(),
		})
	else:
		features['EOS'] = True

	return features

def sent2features(sent):
	return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
	return [label for token, label in sent]

def sent2tokens(sent):
	return [token for token, label in sent]

# load the dataset
X = [sent2features(s) for s in training_set]
y = [sent2labels(s) for s in training_set]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# train the CRF model
crf = sklearn_crfsuite.CRF(
	algorithm='lbfgs',
	c1=0.1,
	c2=0.1,
	max_iterations=100,
	all_possible_transitions=True
)

try:
	crf.fit(X_train, y_train)
except AttributeError:
	pass

# eliminate duplicates of words
def eliminate_duplicates(word):
	# If the word is already in the dictionary, return it as is
	if word.lower() in extended_words:
		return word

	original_word = word
	candidates = [original_word]  # Initialize a list to keep track of word variants

	# Try to eliminate extra letters until the word is found in the dictionary
	while True:
		new_candidates = []
		for candidate in candidates:
			for i in range(len(candidate) - 1, 0, -1):
				# If two consecutive letters are the same, try removing one
				if candidate[i].lower() == candidate[i-1].lower():
					# Generate a new variant with one less character
					new_variant = candidate[:i] + candidate[i+1:]
					if new_variant.lower() in extended_words:
						return new_variant  # Return the new variant if it's in the dictionary
					new_candidates.append(new_variant)

		if not new_candidates:
			break  # Exit the loop if no new candidates can be generated

		candidates = list(set(new_candidates))  # Update the list of candidates, removing duplicates


	# Return the original word if no dictionary word was found
	return original_word

# check spelling
def check_spelling(word):
	spell = Speller(lang='en')
	try:
		new = spell(word)
		return new
	except:
		return word

# normalize using CRF
def normalize_with_crf(original_input, normalize_key):

	temp = [x.lower() for x in original_input]

	for x in range(len(normalize_key)):
		if '&' in temp[x]:
			temp[x] = temp[x].replace('&', 'and')
		elif (normalize_key[x] == 'N') or (temp[x] in emojis_list):

			temp[x] = eliminate_duplicates(temp[x])

			if temp[x] == 'rt':
				temp[x] = "retweet"
			elif temp[x] in abbreviations_list:
				temp[x] = abbreviations_list[temp[x]]
			elif temp[x] in emojis_list:
				temp[x] = emojis_list[temp[x]] + ' emoji'
			elif temp[x] in oov_list:
				temp[x] = oov_list[temp[x]]
			else:
				temp[x] = check_spelling(temp[x])

	output = [x for x in temp if 'http' not in x]

	return " ".join(output)

# normalize using heuristics
def normalize_no_crf(original_input):

	temp = [x.lower() for x in original_input]

	for x in range(len(temp)):
		if ('@' == temp[x][0]) or ('#' == temp[x][0]):
			continue
		elif temp[x] == 'rt':
			temp[x] = "retweet"
		elif '&' in temp[x]:
			temp[x] = temp[x].replace('&', 'and')
		else:

			temp[x] = eliminate_duplicates(temp[x])

			if temp[x] in abbreviations_list:
				temp[x] = abbreviations_list[temp[x]]
			elif temp[x] in emojis_list:
				temp[x] = emojis_list[temp[x]] + ' emoji'
			elif temp[x] in oov_list:
				temp[x] = oov_list[temp[x]]
			else:
				temp[x] = check_spelling(temp[x])

	output = [x for x in temp if 'http' not in x]

	return " ".join(output)


# pipeline with CRF
def pipeline_with_crf(input):
	input_formatted = [(x.lower(), 'none') for x in input]
	test_sentence = sent2features(input_formatted)
	result = crf.predict_single(test_sentence)
	output = normalize_with_crf(input, result)
	return output

# pipeline without CRF
def pipeline_no_crf(input):
	output = normalize_no_crf(input)
	return output



def main(text):
	print("With CRF:", pipeline_with_crf(text))
	print("Without CRF:", pipeline_no_crf(text))

	
if __name__ == '__main__':
  text = input().split()
  main(text)