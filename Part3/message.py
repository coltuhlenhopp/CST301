import requests
from bs4 import BeautifulSoup
import javalang
import json

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# import openai_secret_manager
# import openai

from g4f.client import Client

client = Client()
messages = [
    {"role": "system",
     "content": "You are attempting to classify the inputted description into one of the 31 labels based off of the similarity to it."},
    {"role": "system",
     "content": "As you guess this, your final response should only be one concise paragraph with the label chosen and why."},
    {"role": "system",
     "content": "Answer in the format of: Label: given label of this description"
                "Reason: reason why this label was chosen"}
]


def ask_gpt(class_description, label_options):
    # Construct the prompt with the object description and option descriptions
    prompt = "Does this class description: "
    prompt += f"Object Description: {class_description}\n"
    prompt += " more fit with which of these options: "
    prompt += f"Options: {label_options}\n"
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        stream=True
    )
    return response


# Javax.sql description
description = "Provides the API for server side data source access and processing from the JavaTM programming language."
# Labels and their descriptions
options = {
    "Application": "third party apps or plugins for specific use attached to the system",
    "Application Performance Manager": "monitors performance or benchmark",
    "Big Data": "API's that deal with storing large amounts of data. with variety of formats",
    "Cloud": "APUs for software and services that run on the Internet",
    "Computer Graphics": "Manipulating visual content",
    "Data Structure": "Data structures patterns (e.g., collections, lists, trees)",
    "Databases": "Databases or metadata",
    "Software Development and IT": "Libraries for version control, continuous integration and continuous delivery",
    "Error Handling": "response and recovery procedures from error conditions",
    "Event Handling": "answers to event like listeners",
    "Geographic Information System": "Geographically referenced information",
    "Input/Output": "read, write data",
    "Interpreter": "compiler or interpreter features",
    "Internationalization": "integrate and infuse international, intercultural, and global dimensions",
    "Logic": "frameworks, patterns like commands, controls, or architecture-oriented classes",
    "Language": "internal language features and conversions",
    "Logging": "log registry for the app",
    "Machine Learning": "ML support like build a model based on training data",
    "Microservices/Services": "Independently deployable smaller services. Interface between two different applications so that they can communicate with each other",
    "Multimedia": "Representation of information with text, audio, video",
    "Multithread": "Support for concurrent execution",
    "Natural Language Processing": "Process and analyze natural language data",
    "Network": "Web protocols, sockets RMI APIs",
    "Operating System": "APIs to access and manage a computer's resources",
    "Parser": "Breaks down data into recognized pieces for further analysis",
    "Search": "API for web searching",
    "Security": "Crypto and secure protocols",
    "Setup": "Internal app configurations",
    "User Interface": "Defines forms, screens, visual controls",
    "Utility": "third party libraries for general use",
    "Test": "test automation"
}
gpt_response = ask_gpt(description, options)
counter = 0
answer = ""
for chunk in gpt_response:
    if chunk.choices[0].delta.content:
        answer += (chunk.choices[0].delta.content.strip('*') or "")
print(answer)


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


def summarize_to_one_sentence(paragraph):
    # Initialize the parser with the input paragraph
    parser = PlaintextParser.from_string(paragraph, Tokenizer("english"))

    # Initialize the LSA Summarizer
    summarizer = LsaSummarizer()

    # Summarize the input paragraph to one sentence
    summary = summarizer(parser.document, 1)

    # Extract the summarized sentence
    summarized_sentence = next(summary).text

    return summarized_sentence


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
    base_url = "https://docs.oracle.com/javase/8/docs/api/"
    # Replace periods with slashes in the class/interface name
    class_path = class_or_interface_name.replace('.', '/')
    search_url = f"{base_url}{class_path}.html"
    return search_url



def classify_into_domains(ast_file):
    domains_mapping = {
        "Application": ["App"],
        "Application Performance Manager": ["APM"],
        "Big Data": ["Big Data"],
        "Cloud": ["Cloud"],
        "Computer Graphics": ["CG"],
        "Data Structure": ["Data Structure"],
        "Database": ["DB"],
        "DevOps": ["DevOps"],
        "Error Handling": ["Error Handling"],
        "Event Handling": ["Event Handling"],
        "Geographic Information System": ["GIS"],
        "Input-Output": ["IO"],
        "Interpreter": ["Interpreter"],
        "Internationalization": ["Internationalization"],
        "Logic": ["Logic"],
        "Language": ["Lang"],
        "Logging": ["Logging"],
        "Machine Learning": ["Machine Learning"],
        "Microservices/Services": ["Microservices/Services"],
        "Multimedia": ["Multimedia"],
        "Multi-thread": ["Multi-thread"],
        "Natural Language Processing": ["Natural Language Processing"],
        "Network": ["Network"],
        "Operating System": ["Operating system"],
        "Parser": ["Parser"],
        "Search": ["Search"],
        "Security": ["Security"],
        "Setup": ["Setup"],
        "User Interface": ["User Interface"],
        "Utility": ["Utility"],
        "Test": ["Test"]
    }

    # Load the AST from the provided AST file
    with open(ast_file, 'r') as file:
        ast = json.load(file)

    # Extract information from the AST
    imports = set()
    interesting_things = set()
    variables = set()

    def traverse(node):
        nonlocal imports, interesting_things, variables
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'Import':
                    imports.add(value['path'].split('.')[-1])
                elif key == 'name' and value is not None:
                    variables.add(value.lower())
                elif key == 'MethodDeclaration':
                    if 'name' in value and value['name'] is not None:
                        interesting_things.add(value['name'].lower())
                    for parameter in value.get('parameters', []):
                        if isinstance(parameter, javalang.tree.FormalParameter):
                            if parameter.name is not None:
                                variables.add(parameter.name.lower())
                    traverse(value.get('body', {}))
                elif key == 'VariableDeclarator':
                    if 'name' in value and value['name'] is not None:
                        variables.add(value['name'].lower())
                elif key == 'FieldDeclaration':
                    for variable in value.get('variables', []):
                        if variable.name is not None:
                            variables.add(variable.name.lower())
                elif isinstance(value, (dict, list)):
                    traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    traverse(ast)

    # Identify the classified domains based on extracted information
    classified_domains = set()
    extracted_info = list(interesting_things) + list(variables)
    for info in extracted_info:
        for domain, labels in domains_mapping.items():
            for label in labels:
                if label.lower() in info.lower():
                    classified_domains.add(domain)

    return classified_domains



def add_domain_functions():
    # Define functions related to each domain
    domain_functions = {
        "Database": {
            "java.sql.Connection": ["getConnection(dbcon, user, pswd)", "createStatement()", "prepareStatement(sql)",
                                    "setString(1, pr)", "setString(2, issue)", "setString(3, projName)",
                                    "executeUpdate()", "close()"],
            "java.sql.Statement": ["getConnection(dbcon, user, pswd)", "createStatement()", "prepareStatement(sql)",
                                   "setString(1, pr)", "setString(2, issue)", "setString(3, projName)",
                                   "executeUpdate()", "close()"]
        },
        "Input-Output": {
            "java.io.FileReader": ["read()", "close()"],
            "java.io.FileWriter": ["write(str)", "close()"]
        },
        "Application": {
            "SomeClass": ["someFunction()", "anotherFunction(param)"],
            "AnotherClass": ["someMethod()", "anotherMethod(param)"]
        },
        "Application Performance Manager": {
            "PerformanceMonitor": ["startMonitoring()", "stopMonitoring()", "getPerformanceData()"]
        },
        "Big Data": {
            "BigDataManager": ["storeData(data)", "retrieveData(id)", "analyzeData(data)"]
        },
        "Cloud": {
            "CloudService": ["deployService()", "scaleService()", "monitorService()"]
        },
        "Computer Graphics": {
            "GraphicsRenderer": ["renderScene()", "updateCameraPosition()", "applyLighting()"]
        },
        "Data Structure": {
            "LinkedList": ["add(element)", "remove(index)", "get(index)"],
            "HashMap": ["put(key, value)", "get(key)", "remove(key)"]
        },
        "DevOps": {
            "DeploymentManager": ["deployApp()", "rollbackApp()", "monitorApp()"]
        },
        "Error Handling": {
            "ErrorHandler": ["logError(message)", "notifyAdmin(error)"]
        },
        "Event Handling": {
            "EventDispatcher": ["registerListener(listener)", "dispatchEvent(event)", "removeListener(listener)"]
        },
        "Geographic Information System": {
            "GISProcessor": ["processData(data)", "generateMap(location)", "analyzeTerrain()"]
        },
        "Interpreter": {
            "ScriptInterpreter": ["interpret(script)", "evaluateExpression(expression)", "executeCommand(command)"]
        },
        "Internationalization": {
            "LocalizationManager": ["translate(text)", "formatDate(date)", "getLocale()"]
        },
        "Logic": {
            "RuleEngine": ["addRule(rule)", "evaluateRule(rule)", "removeRule(rule)"]
        },
        "Language": {
            "LanguageProcessor": ["parseText(text)", "generateCode(ast)", "translate(language)"]
        },
        "Logging": {
            "Logger": ["logMessage(message)", "setLogLevel(level)", "flushLogs()"]
        },
        "Machine Learning": {
            "MLModel": ["trainModel(data)", "predictOutcome(input)", "evaluateModel()"]
        },
        "Microservices/Services": {
            "ServiceRegistry": ["registerService(service)", "discoverService(name)", "invokeService(service)"]
        },
        "Multimedia": {
            "MediaProcessor": ["processImage(image)", "playAudio(audio)", "renderVideo(video)"]
        },
        "Multithread": {
            "ThreadManager": ["createThread(task)", "startThread(thread)", "joinThreads(threads)"]
        },
        "Natural Language Processing": {
            "NLPProcessor": ["analyzeText(text)", "extractEntities(text)", "classifyDocument(document)"]
        },
        "Network": {
            "NetworkManager": ["openConnection(url)", "sendRequest(request)", "receiveResponse()"]
        },
        "Operating System": {
            "OSInterface": ["executeCommand(command)", "accessFileSystem(path)", "manageProcesses()"]
        },
        "Parser": {
            "SyntaxParser": ["parseCode(code)", "analyzeSyntax(text)", "generateAST(code)"]
        },
        "Search": {
            "SearchEngine": ["search(query)", "indexDocument(document)", "retrieveResults()"]
        },
        "Security": {
            "SecurityManager": ["encrypt(data)", "decrypt(data)", "authenticateUser(credentials)"]
        },
        "Setup": {
            "SetupManager": ["configureEnvironment(config)", "initializeSystem()", "setupDependencies()"]
        },
        "User Interface": {
            "UIManager": ["displayWindow(window)", "handleInput(event)", "updateUI()"]
        },
        "Utility": {
            "Utilities": ["generateUUID()", "formatDate(date)", "encodeBase64(data)"]
        },
        "Test": {
            "TestSuite": ["runTests()", "addTest(test)", "reportResults()"]
        }
    }
    return domain_functions



def print_domain_functions(classified_domains, domain_functions):
    # Print functions related to classified domains
    for domain in classified_domains:
        if domain in domain_functions:
            print(f"{domain}:")
            for class_name, functions in domain_functions[domain].items():
                print(f"{class_name}:")
                for function in functions:
                    print(f"Function call: {function}")
                print()  # Add a newline after each class's functions
            print()  # Add a newline after each domain's classes


def fetch_definition(domain):
    # Placeholder function to fetch definitions from ChatGPT
    # You can implement this function to call ChatGPT or any other source to fetch definitions
    # For now, let's just return a placeholder message
    return f"Definition for {domain} is not available at the moment."


def print_classified_domain(domain, functions):
    print(f"{domain}:")
    for function, calls in functions.items():
        print(function)
        for call in calls:
            print(f"Function call: {call['name']} ({call['link']})")
    print()


def extract_information(ast_file):
    with open(ast_file, 'r') as file:
        ast = json.load(file)

    imports = set()  # Store import statements
    importPath = set()

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
                    importPath.add(value['path'])
                elif key == 'name' and value is not None:  # Check if 'name' exists and is not None
                    variables.add(value.lower())  # Convert to lowercase
                elif key == 'MethodDeclaration':
                    if 'name' in value and value['name'] is not None:  # Check if 'name' exists and is not None
                        interesting_things.append(value['name'].lower())  # Convert to lowercase
                    for parameter in value.get('parameters',
                                               []):  # Use .get() to handle potential missing 'parameters' key
                        if isinstance(parameter, javalang.tree.FormalParameter):
                            if parameter.name is not None:  # Check if 'name' exists and is not None
                                variables.add(parameter.name.lower())  # Convert to lowercase
                    traverse(value.get('body', {}))  # Use .get() to handle potential missing 'body' key
                elif key == 'VariableDeclarator':
                    if 'name' in value and value['name'] is not None:  # Check if 'name' exists and is not None
                        variables.add(value['name'].lower())  # Convert to lowercase
                elif key == 'FieldDeclaration':
                    for variable in value.get('variables',
                                              []):  # Use .get() to handle potential missing 'variables' key
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
        for i in importPath:
            content = fetch_java_doc_content(fetch_java_doc(i))
            if content is not None:
                file.write(i + ':  \n')
                file.write(content + '\n\n\n')  # Write the content to the file if it's not None

    # Extracting reserved words used in the program by comparing with the predefined list
    used_reserved_words = {identifier for identifier in (interesting_things + list(variables)) if
                           identifier in reserved_words}

    print("Reserved Words:", used_reserved_words)
    print("Interesting Things:", interesting_things)

    # Removes the reserved words from the variables set
    for words in reserved_words:
        if words in variables:
            variables.remove(words)

    print("Variables:", variables)
    '''
    def print_domain_functions(classified_domains, domain_functions):
        for domain in classified_domains:
            if domain in domain_functions:
                print(f"Functions related to the '{domain}' domain:")
                for class_name, functions in domain_functions[domain].items():
                    print(f"{class_name}:")
                    for function in functions:
                        print(f"- {function}")
                print()

    # Call the function to obtain domain functions
    domain_functions = add_domain_functions()

    def print_domain_functions(classified_domains, domain_functions):
        # Print functions related to classified domains
        for domain in classified_domains:
            if domain in domain_functions:
                print(f"Functions related to the '{domain}' domain:")
                for class_name, functions in domain_functions[domain].items():
                    print(f"{class_name}:")
                    for function in functions:
                        print(f"- {function}")
                print()

    # Call the function to print domain functions after extracting information from the AST
    print_domain_functions(classified_domains, domain_functions)
'''

if __name__ == "__main__":
    java_file = "input.java"
    ast_file = "ast.json"

    generate_ast(java_file, ast_file)
    classified_domains = classify_into_domains(ast_file)  # Call classify_into_domains to obtain classified domains
    extract_information(ast_file)
    domain_functions = add_domain_functions()  # Call add_domain_functions to obtain domain functions

    # Only print classified domains and domain functions once
    #print_domain_functions(classified_domains, domain_functions)

    # Step 3: Print out classified domains
    print("Classified Domains List:")
    for domain in classified_domains:
        print(domain)

    print()
    print("Classified Domains, Function Calls, and Definitions:")
    for domain in classified_domains:
        print(domain)

        # Step 4: Print out function calls and their definitions for each classified domain
        if domain in domain_functions:
            for class_name, functions in domain_functions[domain].items():
                print(f"  {class_name}:")
                for function in functions:
                    # Fetch the definition for the function call
                    definition = fetch_definition(function)
                    print(f"    Function call: {function}")
                    print(f"    Definition: {definition}")
                print()  # Add a newline after each class's functions
            print()  # Add a newline after each domain's classes