
from flask import Flask, render_template, request, redirect
import os
import sys

app = Flask(__name__)
folder_path = ''

@app.route('/')
def insertar_formulario(i):
	try:
		with open("t ", "r") as file:
			content = file.read()
			name = file.name
	except FileNotFoundError:
		content = ""
    
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

if __name__ == '__main__':
	#get the path from the first argument
	folder_path = sys.argv[1]
	app.run(debug=True)
