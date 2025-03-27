from flask import Flask, request, jsonify, send_file, render_template
import os
import json
import traceback
import re
from avro_to_dto import generate_main_class, pascal_case
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates", static_folder="static")
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output_dto"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_valid_avro_schema(schema):
    """
    Validates if the provided schema is a valid Avro schema.
    Basic validation checks if:
    1. It's a valid JSON
    2. It has required fields for a record type schema
    3. It follows basic Avro schema structure
    """
    # Check if schema is a dictionary (valid JSON object)
    if not isinstance(schema, dict):
        return False, "Schema must be a JSON object"
    
    # Check for required fields in an Avro record schema
    if "type" not in schema:
        return False, "Schema is missing 'type' field"
    
    if schema["type"] != "record":
        return False, "Schema must have type 'record'"
    
    if "name" not in schema:
        return False, "Schema is missing 'name' field"
    
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', schema["name"]):
        return False, "Schema name must be a valid identifier"
    
    if "fields" not in schema:
        return False, "Schema is missing 'fields' field"
    
    if not isinstance(schema["fields"], list):
        return False, "Schema 'fields' must be an array"
    
    # Check each field
    for field in schema["fields"]:
        if not isinstance(field, dict):
            return False, "Each field must be an object"
        
        if "name" not in field:
            return False, "Field is missing 'name' property"
        
        if "type" not in field:
            return False, "Field is missing 'type' property"
    
    return True, "Valid Avro schema"

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
            
            # Validate Avro schema
            is_valid, message = is_valid_avro_schema(schema)
            if not is_valid:
                return jsonify({'error': f'Invalid Avro schema: {message}'}), 400
                
            print(f"Schema carregado: {schema.get('name', 'unknown')}")
            
            java_code = generate_main_class(schema)
            output_filename = pascal_case(schema["name"]) + "DTO.java"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, 'w') as f:
                f.write(java_code)

            print(f"DTO gerado com sucesso: {output_path}")
            return send_file(output_path, as_attachment=True)

        except json.JSONDecodeError:
            return jsonify({'error': 'The file is not a valid JSON format'}), 400
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