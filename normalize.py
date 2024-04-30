from autocorrect import Speller

# eliminate duplicates of words
def eliminate_duplicates(word, extended_words):
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
def normalize_with_crf(original_input, normalize_key, extended_words, abbreviations_list, emojis_list, oov_list):

	temp = [x.lower() for x in original_input]

	for x in range(len(normalize_key)):
		if '&' in temp[x]:
			temp[x] = temp[x].replace('&', 'and')
		elif (normalize_key[x] == 'N') or (temp[x] in emojis_list):

			temp[x] = eliminate_duplicates(temp[x], extended_words)

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
def normalize_no_crf(original_input, extended_words, abbreviations_list, emojis_list, oov_list):

	temp = [x.lower() for x in original_input]

	for x in range(len(temp)):
		if ('@' == temp[x][0]) or ('#' == temp[x][0]):
			continue
		elif temp[x] == 'rt':
			temp[x] = "retweet"
		elif '&' in temp[x]:
			temp[x] = temp[x].replace('&', 'and')
		else:

			temp[x] = eliminate_duplicates(temp[x], extended_words)

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