
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def insertar_formulario():
    return render_template('index.html')

# gets all the files in the folder and adds them to the left column
@app.route('/open_folder', methods=['POST'])
def open_folder():
	import os
	files = os.listdir('static/files')
	return render_template('index.html', files=files)

if __name__ == '__main__':
	app.run(debug=True)
