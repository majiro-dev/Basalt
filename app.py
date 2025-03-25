
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def insertar_formulario():
	try:
		with open("input1.txt", "r") as file:
			content = file.read()
			name = file.name
	except FileNotFoundError:
		content = ""
		name = ""
    
	return render_template('index.html', content=content, name=name)

# gets all the files in the folder and adds them to the left column
@app.route('/open_folder', methods=['POST'])
def open_folder():
	import os
	files = os.listdir('static/files')
	return render_template('index.html', files=files)


@app.route("/getText", methods=['POST'])
def get_text():
	text = request.form.get("text", "")
	text = text.replace("\n", "")
	with open("input1.txt", "w") as file:
		file.write(text)
	return redirect("/")

if __name__ == '__main__':
	app.run(debug=True)
