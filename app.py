from flask import Flask, request, jsonify, send_file, render_template
import os
import json
import traceback
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
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        print(f"Processando arquivo: {input_path}")
        
        try:
            with open(input_path, 'r') as f:
                schema = json.load(f)
                
            print(f"Schema carregado: {schema.get('name', 'unknown')}")
            
            # Verificando se o schema tem os campos necessários
            if "name" not in schema:
                return jsonify({'error': 'Schema inválido: campo "name" não encontrado'}), 400
            
            if "type" not in schema or schema["type"] != "record":
                return jsonify({'error': 'Schema inválido: deve ser do tipo "record"'}), 400
            
            if "fields" not in schema:
                return jsonify({'error': 'Schema inválido: campo "fields" não encontrado'}), 400

            java_code = generate_main_class(schema)
            output_filename = pascal_case(schema["name"]) + "DTO.java"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, 'w') as f:
                f.write(java_code)

            print(f"DTO gerado com sucesso: {output_path}")
            return send_file(output_path, as_attachment=True)

        except json.JSONDecodeError:
            return jsonify({'error': 'Arquivo não é um JSON válido'}), 400
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"ERRO durante o processamento: {str(e)}\n{error_trace}")
            return jsonify({'error': str(e), 'traceback': error_trace}), 500

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"ERRO na requisição: {str(e)}\n{error_trace}")
        return jsonify({'error': str(e), 'traceback': error_trace}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)