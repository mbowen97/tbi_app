from flask import Flask, render_template, request, jsonify, abort, Response
from flask_cors import CORS
import yaml
import math
import sys

app = Flask(__name__)
CORS(app)

with open("data/model.yml", "r") as stream:
    try:
        model = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open("data/questions.yml", "r") as stream:
    try:
        questions = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

variables = {x: {'raw': list(model[x].keys())} for x in list(model.keys()) if isinstance(model[x], dict)}

for var in variables.keys():
    variables[var]['q'] = questions[var]['q']
    variables[var]['a'] = [questions[var][int(x.rsplit('_',1)[1])] for x in variables[var]['raw']]

questions_dict = {variables[var]['q']: variables[var]['a'] for var in list(variables.keys())}

@app.route('/', methods=['GET'])
def quiz():
    return render_template('main.html', q = questions_dict)

@app.route('/results', methods=['POST'])
def results():
    question_list = list(questions_dict.keys())
    variable_list = list(variables.keys())
    coefs = []
    for i in range(len(questions_dict.keys())):
        state = (variables[variable_list[i]]['raw'][variables[variable_list[i]]['a'].index(request.form[question_list[i]])])
        coefs.append(model[variable_list[i]][state])
    rhs = math.exp(model['Intercept'] + sum(coefs))
    prob = round(rhs/(1 + rhs) * 100, 4)
    if prob >= 0.5:
        rec = 'recommend'
    else:
        rec = 'do not recommend'
    return render_template('results.html', p = prob, r = rec)

@app.route('/model_weights', methods=['GET'])
def get_weights():
    return jsonify(isError=False, message="Success", weights=model)

@app.route('/model_variables', methods=['GET'])
def get_variables():
    return jsonify(isError=False, message="Success", variables=list(model.keys()))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
