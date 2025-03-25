
from flask import Flask, render_template, request, redirect
import os
import sys

app = Flask(__name__)
folder_path = ''

@app.route('/')
def insertar_formulario():
	try:
		with open("input1.txt ", "r") as file:
			content = file.read()
			name = file.name
	except FileNotFoundError:
		content = ""
		name = ""
	return render_template('index.html', content=content, name=name)

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
	with open("input1.txt", "w") as file:
		file.write(text)
	#print(f"Texto recebido: {text}")
	return redirect("/")

# ****** Tareas ********

@app.route('/tasks')
def tasks():
    tasks = load_tasks()
    return render_template('tasks.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    tasks = load_tasks()
    tasks.append({'id': len(tasks) + 1, 'name': task_name, 'completed': False})
    save_tasks(tasks)
    return redirect('/tasks')

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return redirect('/tasks')

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    return redirect('/tasks')

@app.route('/save_tasks', methods=['POST'])
def save_tasks_route():
    tasks = request.json['tasks']
    save_tasks(tasks)
    return jsonify({'status': 'success'})

@app.route('/create_task_list', methods=['POST'])
def create_task_list():
    task_list_name = request.form['task_list_name']
    if not os.path.exists('task_lists'):
        os.makedirs('task_lists')
    with open(f'task_lists/{task_list_name}.json', 'w') as f:
        json.dump([], f)
    return redirect('/tasks')

def load_tasks():
    if os.path.exists('tasks.json'):
        with open('tasks.json', 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f)

# ***********************************************

if __name__ == '__main__':
	#get the path from the first argument
	folder_path = sys.argv[1]
	app.run(debug=True)
