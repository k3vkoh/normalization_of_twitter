import setup
import crf
import normalize
from sklearn.model_selection import train_test_split

training_set = setup.return_training_set()
abbrev = setup.return_abbreviations()
emojis = setup.return_emojis()
oov = setup.return_oov()
extended_words = setup.return_extended_words()

# load the dataset
X = [crf.sent2features(s) for s in training_set]
y = [crf.sent2labels(s) for s in training_set]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

our_crf = crf.train_crf(X_train, y_train)

# pipeline with CRF
def pipeline_with_crf(input):
	input_formatted = [(x.lower(), 'none') for x in input]
	test_sentence = crf.sent2features(input_formatted)
	result = our_crf.predict_single(test_sentence)
	output = normalize.normalize_with_crf(input, result, extended_words, abbrev, emojis, oov)
	return output

# pipeline without CRF
def pipeline_no_crf(input):
	output = normalize.normalize_no_crf(input, extended_words, abbrev, emojis, oov)
	return output

# main function for testing
def main(text):
	print("With CRF:", pipeline_with_crf(text))
	print("Without CRF:", pipeline_no_crf(text))

if __name__ == '__main__':
  print('Enter a sentence:')
  text = input().split()
  main(text)