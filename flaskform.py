import flask
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import deid_client
import json
import zipfile
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100*1024*1024

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submitText', methods=['POST'])
def submitText():
    # run client
    highlight_words = []
    input_text = request.form['input_text'].encode('utf8')
    predictions, results, sentences = deid_client.run_client(input_text)

    for i in range(len(results)):
        for j in range(len(results[i])):
            if results[i][j][1] != "O":
                highlight_words.append(results[i][j][0])

    return render_template('result.html', result=results, text = input_text, data =json.dumps(highlight_words))



@app.route('/upload_files', methods =['GET', 'POST'])
def upload_files():

    dst= "results_folder"
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if request.method == 'POST' and 'text' in request.files:
        zf = zipfile.ZipFile("%s/%s.zip" % (dst, timestr), "w", zipfile.ZIP_DEFLATED)

        for f in request.files.getlist('text'):
            filename = secure_filename(f.filename)
            full_filename = os.path.join("uploaded_folder", filename)
            f.save(full_filename)

            result_path =deid_client.run_on_textfile(full_filename)

            zf.write(result_path, "deid_"+filename)
        zf.close()

        return redirect(url_for('download_deid_files', timestr = timestr))

@app.route('/download_deid_files/<timestr>', methods = ['GET'])
def download_deid_files(timestr):
    print(timestr)
    return flask.send_from_directory('results_folder', '%s.zip'%timestr, attachment_filename ='%s.zip'%timestr, as_attachment=True)


