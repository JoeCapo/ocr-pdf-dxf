from flask import Flask, request, redirect, url_for, send_file, render_template, flash, jsonify
from werkzeug.utils import secure_filename
import os
import ocr_utils
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'dxf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if filename.lower().endswith('.pdf'):
            texts = ocr_utils.extract_text_from_pdf(filepath)
            df = pd.DataFrame({'Extracted Text': texts})
        elif filename.lower().endswith('.dxf'):
            data = ocr_utils.extract_data_from_dxf(filepath)
            df = pd.DataFrame(data)

        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0] + '.xlsx')
        df.to_excel(excel_path, index=False)

        return jsonify({'texts': df.to_dict(orient='records'), 'excel_path': excel_path})


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
