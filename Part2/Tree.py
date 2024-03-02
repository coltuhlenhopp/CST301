import requests
from bs4 import BeautifulSoup
import javalang
import json

def fetch_java_doc_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the relevant section containing the content
            content_section = soup.find('div', class_='block')
            if content_section:
                # Extract the text content
                return content_section.get_text(separator='\n')
            else:
                print(f"Failed to find content section on {url}")
        else:
            print(f"Failed to fetch content from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching content from {url}: {e}")
    return None


def generate_ast(java_file, output_file):
    with open(java_file, 'r') as file:
        java_code = file.read()

    tree = javalang.parse.parse(java_code)

    # Convert the tree to a dictionary
    ast_dict = tree_to_dict(tree)

    with open(output_file, 'w') as out_file:
        json.dump(ast_dict, out_file, default=str, indent=4)  # Use default=str for non-serializable objects

def tree_to_dict(tree):
    if isinstance(tree, (javalang.tree.Node, javalang.tree.CompilationUnit)):
        return {tree.__class__.__name__: {k: tree_to_dict(v) for k, v in tree.__dict__.items() if k != 'children'}}
    elif isinstance(tree, list):
        return [tree_to_dict(item) for item in tree]
    elif isinstance(tree, tuple):
        return {k: tree_to_dict(v) for k, v in tree._asdict().items()}
    elif isinstance(tree, set):
        return list(tree)
    else:
        return str(tree)

def fetch_java_doc(class_or_interface_name):
    # Adjusted to use a more generic and correct URL forming method
    base_url = "https://docs.oracle.com/javase/8/docs/api/java/util/"
    search_url = f"{base_url}{class_or_interface_name.replace('.', '/')}.html"
    return search_url

def extract_information(ast_file):
    with open(ast_file, 'r') as file:
        ast = json.load(file)

    imports = set()  # Store import statements

    # Manually compiled list of Java reserved words
    reserved_words = {
        'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue',
        'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'if', 'goto',
        'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'package', 'private',
        'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this',
        'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while'
    }

    interesting_things = []
    variables = set()

    def traverse(node):
        nonlocal imports, interesting_things, variables
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'Import':
                    imports.add(value['path'].split('.')[-1])  # Extract the last part of the import path
                elif key == 'name' and value is not None:  # Check if 'name' exists and is not None
                    variables.add(value.lower())  # Convert to lowercase
                elif key == 'MethodDeclaration':
                    if 'name' in value and value['name'] is not None:  # Check if 'name' exists and is not None
                        interesting_things.append(value['name'].lower())  # Convert to lowercase
                    for parameter in value.get('parameters', []):  # Use .get() to handle potential missing 'parameters' key
                        if isinstance(parameter, javalang.tree.FormalParameter):
                            if parameter.name is not None:  # Check if 'name' exists and is not None
                                variables.add(parameter.name.lower())  # Convert to lowercase
                    traverse(value.get('body', {}))  # Use .get() to handle potential missing 'body' key
                elif key == 'VariableDeclarator':
                    if 'name' in value and value['name'] is not None:  # Check if 'name' exists and is not None
                        variables.add(value['name'].lower())  # Convert to lowercase
                elif key == 'FieldDeclaration':
                    for variable in value.get('variables', []):  # Use .get() to handle potential missing 'variables' key
                        if variable.name is not None:  # Check if 'name' exists and is not None
                            variables.add(variable.name.lower())  # Convert to lowercase
                elif isinstance(value, (dict, list)):
                    traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    traverse(ast)

    print("Imports:", imports)

    with open("JavaDoc.txt", "w") as file:
        for i in imports:
            content = fetch_java_doc_content(fetch_java_doc(i))
            if content is not None:
                file.write(i + ':  \n')
                file.write(content + '\n\n\n')  # Write the content to the file if it's not None


    # Extracting reserved words used in the program by comparing with the predefined list
    used_reserved_words = {identifier for identifier in (interesting_things + list(variables)) if identifier in reserved_words}

    print("Reserved Words:", used_reserved_words)

    print("Interesting Things:", interesting_things)

    # Removes the reserved words from the variables set
    for words in reserved_words:
        if words in variables:
            variables.remove(words)

    print("Variables:", variables)

if __name__ == "__main__":
    java_file = "input.java"
    ast_file = "ast.json"

    generate_ast(java_file, ast_file)
    extract_information(ast_file)



