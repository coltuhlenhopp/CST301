# Colt Uhlenhopp
# 2/13/2024

import json
import os
import javalang

def clean_ast_path(path):
    # Convert the path string to a list of node names
    return [node.__class__.__name__ for node in path]

def print_ast(java_file_path, output_file_path):
    # Parse the Java source file into an AST
    with open(java_file_path, "r") as file:
        java_source_code = file.read()
    # Parses out the java nodes
    ast = javalang.parse.parse(java_source_code)

    # Create a list to store the AST nodes
    ast_nodes = []

    # Iterate over AST nodes and append their essential information to the list
    for path, node in ast:
        node_info = {
            "path": clean_ast_path(path),
            "type": node.__class__.__name__
        }
        if hasattr(node, "position"):
            node_info["position"] = str(node.position)
        ast_nodes.append(node_info)

    # Write the AST nodes list to a JSON file
    with open(output_file_path, "w") as json_file:
        json.dump(ast_nodes, json_file, indent=4)

def main():
    # Path to the input Java source file
    java_file_path = "input.java"

    # Output file path for the JSON representation of the AST
    output_file_path = "ast.json"

    # Print the AST to a JSON file
    print_ast(java_file_path, output_file_path)
    print("AST has been written to", os.path.abspath(output_file_path))

if __name__ == "__main__":
    main()

