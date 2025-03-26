import json
import sys
import os
from typing import Any, Dict, List, Tuple

def pascal_case(s: str) -> str:
    return ''.join(word.capitalize() for word in s.replace('_', ' ').split())

def avro_type_to_java(avro_type: Any, nested_classes: Dict[str, Any]) -> str:
    if isinstance(avro_type, list):
        non_null = [t for t in avro_type if t != 'null']
        if not non_null:  # Proteção contra listas vazias
            return "Object"
        return avro_type_to_java(non_null[0], nested_classes)

    if isinstance(avro_type, dict):
        # Verifica se o dicionário tem a chave "type"
        if "type" not in avro_type:
            print(f"Aviso: Dicionário sem chave 'type': {avro_type}")
            return "Object"
            
        t = avro_type["type"]
        
        # Lidar com tipos lógicos
        if "logicalType" in avro_type:
            logical_type = avro_type["logicalType"]
            if logical_type == "timestamp-millis" or logical_type == "timestamp-micros":
                return "java.time.Instant"
            elif logical_type == "date":
                return "java.time.LocalDate"
            elif logical_type == "time-millis" or logical_type == "time-micros":
                return "java.time.LocalTime"
        
        if t == "record":
            name = pascal_case(avro_type["name"]) + "DTO"
            # Usar uma string como chave em vez do dicionário
            # Armazenamos o schema para processamento posterior, não durante a iteração
            nested_classes[name] = avro_type.copy()  # Importante: usamos uma cópia do dicionário
            return name
        elif t == "enum":
            name = pascal_case(avro_type["name"])
            # Armazenamos o schema para processamento posterior, não durante a iteração
            nested_classes[name] = avro_type.copy()  # Importante: usamos uma cópia do dicionário
            return name
        elif t == "array":
            return f"List<{avro_type_to_java(avro_type['items'], nested_classes)}>"
        elif t == "map":
            return f"Map<String, {avro_type_to_java(avro_type['values'], nested_classes)}>"
    
    # Tipos Avro primitivos mapeados para tipos Java
    return {
        "string": "String",
        "int": "int",
        "long": "long",
        "float": "float",
        "double": "double",
        "boolean": "boolean",
        "bytes": "byte[]",
        "null": "Void"
    }.get(avro_type, "Object")

def generate_field_code(field: Dict[str, Any], nested_classes: Dict[str, Any]) -> Tuple[str, str, str]:
    name = field["name"]
    java_type = avro_type_to_java(field["type"], nested_classes)
    field_line = f"    private {java_type} {name};"

    getter = f"""
    public {java_type} get{pascal_case(name)}() {{
        return {name};
    }}"""
    setter = f"""
    public void set{pascal_case(name)}({java_type} {name}) {{
        this.{name} = {name};
    }}"""
    
    return field_line, getter, setter

def generate_nested_classes(nested_classes: Dict[str, Any]) -> str:
    code_blocks = []
    
    # Fazemos uma cópia das chaves para evitar mudanças durante a iteração
    class_names = list(nested_classes.keys())
    
    for class_name in class_names:
        schema = nested_classes[class_name]
        
        if schema["type"] == "record":
            fields = schema.get("fields", [])
            lines = [f"    public static class {class_name} {{"]
            constructor_params = []
            constructor_body = []
            getters_setters = []
            
            # Processamos cada campo do registro
            for field in fields:
                field_line, getter, setter = generate_field_code(field, nested_classes)
                lines.append("        " + field_line.strip())
                field_name = field["name"]
                java_type = avro_type_to_java(field["type"], nested_classes)
                constructor_params.append(f"{java_type} {field_name}")
                constructor_body.append(f"            this.{field_name} = {field_name};")
                getters_setters.append("    " + getter.strip())
                getters_setters.append("    " + setter.strip())

            lines.append("")
            if constructor_params:
                lines.append(f"        public {class_name}({', '.join(constructor_params)}) {{")
                lines.extend(constructor_body)
                lines.append("        }")

            lines.extend(getters_setters)
            lines.append("    }")
            code_blocks.append("\n".join(lines))

        elif schema["type"] == "enum":
            enum_name = pascal_case(schema["name"])
            symbols = ', '.join(schema["symbols"])
            code_blocks.append(f"    public static enum {enum_name} {{ {symbols} }}")

    return "\n\n".join(code_blocks)

def process_all_nested_schemas(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Pré-processa todos os esquemas aninhados recursivamente."""
    nested_classes = {}
    
    def process_schema(avro_type: Any) -> None:
        if isinstance(avro_type, list):
            for t in avro_type:
                if t != 'null':
                    process_schema(t)
        elif isinstance(avro_type, dict):
            if "type" not in avro_type:
                return
                
            t = avro_type["type"]
            
            if t == "record":
                name = pascal_case(avro_type["name"]) + "DTO"
                nested_classes[name] = avro_type
                
                # Processa campos recursivamente
                for field in avro_type.get("fields", []):
                    process_schema(field.get("type"))
            elif t == "enum":
                name = pascal_case(avro_type["name"])
                nested_classes[name] = avro_type
            elif t == "array":
                process_schema(avro_type.get("items"))
            elif t == "map":
                process_schema(avro_type.get("values"))
    
    # Processa o esquema principal
    for field in schema.get("fields", []):
        process_schema(field.get("type"))
        
    return nested_classes

def generate_main_class(schema: Dict[str, Any]) -> str:
    class_name = pascal_case(schema["name"]) + "DTO"
    fields = schema.get("fields", [])

    # Pré-processa todos os esquemas aninhados para evitar o problema de modificação durante iteração
    nested_classes = process_all_nested_schemas(schema)

    imports = set()
    field_lines = []
    constructor_params = []
    constructor_body = []
    getters_setters = []

    for field in fields:
        field_line, getter, setter = generate_field_code(field, nested_classes)
        field_lines.append(field_line)
        java_type = avro_type_to_java(field["type"], nested_classes)
        field_name = field["name"]
        if "List<" in java_type:
            imports.add("import java.util.List;")
        if "Map<" in java_type:
            imports.add("import java.util.Map;")
        if "java.time." in java_type:
            imports.add(f"import {java_type};")
        constructor_params.append(f"{java_type} {field_name}")
        constructor_body.append(f"        this.{field_name} = {field_name};")
        getters_setters.append(getter)
        getters_setters.append(setter)

    class_lines = []
    if imports:
        class_lines.append("\n".join(sorted(imports)))
        class_lines.append("")

    class_lines.append(f"public class {class_name} {{")
    class_lines.extend(field_lines)
    class_lines.append("")
    if constructor_params:
        class_lines.append(f"    public {class_name}({', '.join(constructor_params)}) {{")
        class_lines.extend(constructor_body)
        class_lines.append("    }")
        class_lines.append("")
    class_lines.extend(getters_setters)

    # Add nested classes
    nested_code = generate_nested_classes(nested_classes)
    if nested_code:
        class_lines.append("")
        class_lines.append(nested_code)

    class_lines.append("}")

    return "\n".join(class_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python avro_to_single_dto.py <schema_file.avsc>")
        return

    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        schema = json.load(f)

    java_code = generate_main_class(schema)

    output_dir = "output_dto"
    os.makedirs(output_dir, exist_ok=True)

    top_class_name = pascal_case(schema["name"]) + "DTO.java"
    with open(os.path.join(output_dir, top_class_name), 'w') as f:
        f.write(java_code)

    print(f"✅ Generated single DTO file: output_dto/{top_class_name}")

if __name__ == "__main__":
    main()