from flask import Flask, render_template, request, redirect, jsonify
import os
import sys
import json

app = Flask(__name__)
folder_path = ''
current_file = ''

@app.route('/')
def insertar_formulario():
	try:
		with open(folder_path + "/" + current_file , "r") as file:
			content = file.read()
			name = file.name
	except FileNotFoundError:
		content = ""
		name = ""
	return render_template('index.html', content=content, name=name)

@app.route('/open_file', methods=['GET'])
def open_file():
	global current_file
	current_file = request.args.get("file")
	print(current_file + " opened")
	return redirect("/")

# return the file paths from the files in the folder
@app.route('/get_files')
def get_files():
	files = []
	for file in os.listdir(folder_path):
		if os.path.isfile(os.path.join(folder_path, file)):
			files.append(file)
	return files


@app.route("/getText", methods=['POST'])
def get_text():
	text = request.form.get("text", "")
	text = text.replace("\n", "")
	with open(folder_path + "/" + current_file , "w") as file:
		file.write(text)
	return redirect("/")


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


# ***********************************************


def init():
	global folder_path
	global current_file
	#get the path from the first argument
	folder_path = sys.argv[1]
	# current file is the first file in the folder or if it is empty, create a new file named "new_note.txt"
	files = os.listdir(folder_path)
	if len(files) > 0:
		current_file = files[0]
	else:
		current_file = "new_note.txt"
		with open(folder_path + "/" + current_file , "w") as file:
			file.write("")


if __name__ == '__main__':
	init()
	app.run(debug=True)

