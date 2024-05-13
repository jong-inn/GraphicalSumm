import os
import logging
import subprocess
from flask import Flask
from celery import Celery
from flask import Flask, request, url_for, redirect, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


UPLOAD_FOLDER = './data/audio/raw'
# ALLOWED_EXTENSIONS = {'mp3', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    try:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    except:
        return jsonify({'error': 'Something went wrong'}), 400

@app.route('/runscript')
def run_script():
    try:
        # Define the path to your script
        script_path = '/path/to/your/script.sh'
        
        # Running the script
        result = subprocess.run(['bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Checking if the script ran successfully
        if result.returncode == 0:
            return f"Script executed successfully: {result.stdout}"
        else:
            return f"Script execution failed: {result.stderr}"
    except Exception as e:
        return str(e)

@celery.task
def long_running_task():
    info = request.get_json(force=True)
    file_name = info['file_name']
    
    # Your long-running task here
    script_path = './scripts/transcribe.sh'
    
    command = ['bash', script_path, file_name]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        return f"Script executed successfully: {result.stdout}"
    else:
        return f"Script execution failed: {result.stderr}"

@app.route('/run', methods=['POST'])
def run():
    app.logger.info("Request running tasks.")
    
    info = request.get_json(force=True)
    file_name = info['file_name']
    
    script_path = './scripts/transcribe.sh'
    
    command = ['bash', script_path, file_name]
    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = {
            'status': 200
        }
    except Exception as e:
        app.logger.info(e)
        data = {
            'status': 400
        }
    
    response = jsonify(data)
    print(data)
    
    return response

@app.route('/start-task', methods=['POST'])
def start_task():
    task = long_running_task.delay()
    return jsonify({'task_id': task.id}), 202

@app.route('/task-status/<task_id>')
def task_status(task_id):
    task = long_running_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'result': task.result
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=3001, debug=False)