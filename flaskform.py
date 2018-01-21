from flask import Flask, request, render_template
import deid_client
import json
app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submitText', methods=['POST'])
def submitText():
    # run client
    highlight_words = []
    input_text = request.form['input_text'].encode('utf8')
    predictions, results = deid_client.run_client(input_text)

    for i in range(len(results)):
        for j in range(len(results[i])):
            if results[i][j][1] != "O":
                highlight_words.append(results[i][j][0])



    return render_template('result.html', result=results, text = input_text, data =json.dumps(highlight_words))

