import sklearn_crfsuite

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

def train_crf(X_train, y_train):
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
		return crf
	except AttributeError:
		return None