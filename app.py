from flask import Flask, render_template, request, jsonify
import pipeline

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/normalize', methods=['POST'])
def predict():
	sentence = request.json['userInput'].split() 
	option = request.json['option']
	if option == 'nocrf':
		result = pipeline.pipeline_no_crf(sentence)
	else:
		result = pipeline.pipeline_with_crf(sentence)
	return jsonify(result=result)

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(debug=True)