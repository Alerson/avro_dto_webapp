from flask import Flask, request, jsonify, send_file, render_template
import os
import json
from avro_to_dto import generate_main_class, pascal_case
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output_dto"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate-dto', methods=['POST'])
def generate_dto():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        with open(input_path, 'r') as f:
            schema = json.load(f)

        java_code = generate_main_class(schema)
        output_filename = pascal_case(schema["name"]) + "DTO.java"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, 'w') as f:
            f.write(java_code)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)