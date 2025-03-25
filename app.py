
from flask import Flask, render_template, request, redirect
import os
import sys

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
	#print(f"Texto recebido: {text}")
	return redirect("/")

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
