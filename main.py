import streamlit as st
import json
class Formatter:
    def __init__(self, className="Generate"):
        self.className = className
        self.generated_classes = {}

    def json_to_dart(self, jsonObj):
        # Generate the Dart code for the main class
        main_class_code = self._generate_dart_class(self.className, jsonObj)
        
        # Combine all generated classes
        full_dart_code = "\n\n".join([code for _, code in self.generated_classes.items()])
        # return full_dart_code + "\n\n" + main_class_code
        return full_dart_code

    def _generate_dart_class(self, class_name, json_obj):
        if class_name in self.generated_classes:
            return ""

        def dart_type(value, key):
            if isinstance(value, int):
                return "int"
            elif isinstance(value, float):
                return "double"
            elif isinstance(value, bool):
                return "bool"
            elif isinstance(value, dict):
                # nested_class_name = f"{class_name}{key.capitalize()}"
                nested_class_name = f"{key.capitalize()}"
                self._generate_dart_class(nested_class_name, value)
                return nested_class_name
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    # nested_class_name = f"{class_name}{key.capitalize()}"
                    nested_class_name = f"{key.capitalize()}"
                    self._generate_dart_class(nested_class_name, value[0])
                    return f"List<{nested_class_name}>"
                elif len(value) > 0:
                    return f"List<{dart_type(value[0], key)}>"
                else:
                    return "List<dynamic>"
            else:
                return "String"

        # Start building the Dart class string
        dartCode = f"class {class_name} {{\n"
        
        # Declare variables
        for key, value in json_obj.items():
            dartCode += f"  final {dart_type(value, key)}? {key};\n"
        
        # Constructor
        dartCode += f"\n  {class_name}({{"
        dartCode += ", ".join([f"required this.{key}" for key in json_obj.keys()])
        dartCode += "});\n"
        
        # fromJson factory method
        dartCode += f"\n  factory {class_name}.fromJson(Map<String, dynamic> json) => {class_name}(\n"
        for key, value in json_obj.items():
            if isinstance(value, dict):
                # nested_class_name = f"{class_name}{key.capitalize()}"
                nested_class_name = f"{key.capitalize()}"
                dartCode += f"    {key}: json['{key}'] != null ? {nested_class_name}.fromJson(json['{key}']) : null,\n"
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # nested_class_name = f"{class_name}{key.capitalize()}"
                nested_class_name = f"{key.capitalize()}"
                dartCode += f"    {key}: json['{key}'] != null ? List<{nested_class_name}>.from(json['{key}'].map((x) => {nested_class_name}.fromJson(x))) : null,\n"
            else:
                dartCode += f"    {key}: json['{key}'],\n"
        dartCode += "  );\n"
        
        # toJson method
        dartCode += f"\n  Map<String, dynamic> toJson() => {{\n"
        for key, value in json_obj.items():
            if isinstance(value, dict):
                dartCode += f"    '{key}': {key}?.toJson(),\n"
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                dartCode += f"    '{key}': {key}?.map((x) => x.toJson()).toList(),\n"
            else:
                dartCode += f"    '{key}': {key},\n"
        dartCode += "  };\n"
        
        # Close class
        dartCode += "}\n"

        # Store the generated class code
        self.generated_classes[class_name] = dartCode
        return dartCode

    def make_service(self):
        dartCode = f'''
Future<Response> test() async {{
    final response = await Requests(
        method: Requests.get,
        url: 'https://dummyjson.com/test',
        isAuth: false,
    ).send();
    print('https://dummyjson.com/test');
    return response;
}}'''
        return dartCode;

  
# Set up the page
st.set_page_config(page_title="JSON to Dart Model Converter", layout="centered")
st.title("JSON to Dart Model Converter")
st.text("Paste your JSON data below, and this tool will generate Dart model classes.")

# Input JSON data
jsonInput = st.text_area("Enter JSON data", placeholder='{"name": "John", "age": 30, "city": "New York"}')
classNameInput = st.text_input("Enter class name", value="Generate")

if st.button("Generate Dart Model", type="primary"):
    try:
        jsonData = json.loads(jsonInput)
        formatter = Formatter(classNameInput)

        # Generate Dart code
        if isinstance(jsonData, dict):
            dartCode = formatter.json_to_dart(jsonData)
            st.code(dartCode, language="dart", line_numbers=True)
        else:
            st.error("The JSON data should represent an object (a dictionary in Python).")
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your input.")

