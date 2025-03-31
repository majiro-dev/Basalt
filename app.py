from flask import Flask, render_template, request, redirect, jsonify
import os
import sys
import json
import markdown
import markdownify
import re

app = Flask(__name__)
folder_path = ''
current_file = ''
message = ''

@app.route('/')
def insertar_formulario():
    global folder_path
    content = "No file"
    path = ''
    name = "No file"
    if folder_path and os.path.exists(folder_path):
        file_path = os.path.join(folder_path, current_file)
        path = folder_path
        if current_file and os.path.exists(file_path):
            try:
                with open(folder_path + "/" + current_file , "r") as file:
                    content = file.read()
                    content = markdown_to_html(content)
                    content = readd_links(content)
                    #print(content)
                    name = current_file
            except FileNotFoundError:
                content = "No file"
                name = "No file"
        elif current_file != "":
            #create the file if it does not exist
            with open(folder_path + "/" + current_file , "w") as file:
                file.write("")
                content = ""
                name = current_file

    else:
        path = folder_path + " no such folder"
    return render_template('index.html', content=content, name=name, message=message, path=path)

#abre un archivo
@app.route('/open_file', methods=['GET'])
def open_file():
	global current_file
	current_file = request.args.get("file")
	return redirect("/")

# return the file paths from the files in the folder
@app.route('/get_files')
def get_files():
	files = []
	for file in os.listdir(folder_path):
		if os.path.isfile(os.path.join(folder_path, file)):
			files.append(file)
	return files

#rename the file
@app.route("/rename", methods=['POST'])
def rename_file():
    global current_file
    name = request.form.get("newname", "")
    if (current_file != name and not os.path.exists((os.path.join(folder_path, name)))):
        os.rename(os.path.join(folder_path, current_file), os.path.join(folder_path, name))
        current_file = name
    return redirect("/")

#crea un archivo o abre uno que existe
@app.route("/getFile", methods=['POST'])
def get_file():
    global current_file

    name = request.form.get("filename", "")
    if os.path.exists((os.path.join(folder_path, name))):
        current_file = name
    else:    
        with open(folder_path + "/" + current_file , "w") as file:
            current_file = name
            file.write("")
    return redirect("/")

#guarda el texto en un archivo
@app.route("/getText", methods=['POST'])
def get_text():
    text = request.form.get("text", "")
    text = replace_links(text)
    text = html_to_markdown(text)
    if(os.path.exists((folder_path + "/" + current_file)) and not os.path.isdir((folder_path + "/" + current_file))):
        with open(folder_path + "/" + current_file , "w") as file:
            file.write(text)
    return redirect("/")

#seleciona una carpeta
@app.route('/select_folder', methods=['POST'])
def select_folder():
    global folder_path
    global message
    
    folder_path = request.form.get('folder_path', '')
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        message = "Insert a folder"
        return redirect('/')
    else:
        message = "Error: no folder"
        return redirect('/')
        

# ****** Tareas ********

@app.route('/tasks')
def tasks():
    task_lists = get_task_lists()
    tasks = []
    if task_lists:
        tasks = load_tasks(task_lists[0])
    return render_template('tasks.html', tasks=tasks, task_lists=task_lists)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    task_list_name = request.form['task_list_name']
    tasks = load_tasks(task_list_name)
    tasks.append({'id': len(tasks) + 1, 'name': task_name, 'completed': False})
    save_tasks(task_list_name, tasks)
    return redirect('/tasks')

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task_list_name = request.form['task_list_name']
    tasks = load_tasks(task_list_name)
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(task_list_name, tasks)
    return redirect('/tasks')

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task_list_name = request.form['task_list_name']
    tasks = load_tasks(task_list_name)
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(task_list_name, tasks)
    return redirect('/tasks')

@app.route('/save_tasks/<task_list_name>', methods=['POST'])
def save_tasks_route(task_list_name):
    tasks = request.json['tasks']
    save_tasks(task_list_name, tasks)
    return jsonify({'status': 'success'})

@app.route('/create_task_list', methods=['POST'])
def create_task_list():
    task_list_name = request.json['task_list_name']
    if not os.path.exists('task_lists'):
        os.makedirs('task_lists')
    with open(f'task_lists/{task_list_name}.json', 'w') as f:
        json.dump([], f)  # Inicializar el archivo con un array vacío
    return jsonify({'status': 'success'})

@app.route('/load_tasks/<task_list_name>', methods=['GET'])
def load_tasks_route(task_list_name):
    tasks = load_tasks(task_list_name)
    return jsonify({'tasks': tasks})

def get_task_lists():
    if not os.path.exists('task_lists'):
        return []
    return [f.replace('.json', '') for f in os.listdir('task_lists') if f.endswith('.json')]

def load_tasks(task_list_name):
    if os.path.exists(f'task_lists/{task_list_name}.json'):
        with open(f'task_lists/{task_list_name}.json', 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  # Retornar un array vacío si el archivo está vacío o no es un JSON válido
    return []

def save_tasks(task_list_name, tasks):
    with open(f'task_lists/{task_list_name}.json', 'w') as f:
        json.dump(tasks, f)

@app.route('/delete_task_list/<task_list_name>', methods=['DELETE'])
def delete_task_list(task_list_name):
    file_path = f'task_lists/{task_list_name}.json'
    if os.path.exists(file_path):
        os.remove(file_path)  # Elimina el archivo de la lista de tareas
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Lista no encontrada'}), 404
        
# ***********************************************


# replace text with this format &nbsp;<a href="/open_file?file=b" target="b">b</a> to [[b]]
# to [[b]]
def replace_links(text):
    return re.sub(r'<a href="/open_file\?file=(.*?)">.*?</a>', r'[[\1]]', text)

## replace [[b]] with <a href="/open_file?file=b">b</a>
def readd_links(text):
    matches = re.findall(r'\[\[(.*?)\]\]', text)
    for match in matches:
       text = text.replace("[[" + match + "]]", "<a href=\"/open_file?file=" + match + "\">" + match + "</a>")
    return text

def markdown_to_html(text):
    return markdown.markdown(text)

def html_to_markdown(text):
    return markdownify.markdownify(text)

def init():
    global folder_path
    global current_file
    global message
    message = "Insert a folder"
    folder_path = ""
    current_file = ""


if __name__ == '__main__':
	init()
	app.run(debug=True)

