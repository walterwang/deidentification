from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import deid_client
import zipfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100*1024*1024


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/submit_text', methods=['GET'])
def submit_text():

    input_text = request.args.get('input_text',0, type=None).encode('utf-8')
    show_bio = request.args.get('show_bio', 0, type=None)

    deided_text = deid_client.run_on_text(input_text, eval(show_bio))

    return jsonify(deided_text=deided_text)


@app.route('/upload_files', methods =['GET', 'POST'])
def upload_files():

    dst = "results_folder"

    zip_name = eval(request.form['zip_name'])
    show_bio = eval(request.form['show_bio'])

    if request.method == 'POST':

        zf = zipfile.ZipFile("%s/%d.zip" % (dst, zip_name), "w", zipfile.ZIP_DEFLATED)

        for f in request.files.getlist('text'):
            filename = secure_filename(f.filename)
            full_filename = os.path.join("uploaded_folder", filename)
            f.save(full_filename)
            result_path = deid_client.run_on_textfile(full_filename, show_bio)

            zf.write(result_path, "deid_"+filename)
        zf.close()

    return "ok" # return something so flask doesn't get upset


@app.route('/download_deid_files/<timestr>', methods=['GET'])
def download_deid_files(timestr):
    return send_from_directory('results_folder',
                                     '%s.zip' % timestr,
                                     attachment_filename ='%s.zip' % timestr,
                                     as_attachment=True)

