import os
import json
import time
import logging
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import io
import uuid

app = Flask(__name__)
CORS(app)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# In-memory dictionaries for task statuses and messages
task_statuses = {}
task_messages = {}

# Lock for thread-safe operations
lock = threading.Lock()

@app.route('/create_queue', methods=['POST'])
def create_queue():
    # No longer needed
    pass

@app.route('/produce', methods=['POST'])
def produce_message():
    # No longer needed
    pass

@app.route('/consume', methods=['GET'])
def consume_message():
    # No longer needed
    pass

# File upload settings
UPLOAD_FOLDER = './data/audio/raw'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part in the request')
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    # Copy the file data to an in-memory buffer
    file_data = io.BytesIO(file.read())
    filename = secure_filename(file.filename)

    # Start the thread with the file data buffer
    threading.Thread(target=save_file, args=(file_data, filename)).start()
    app.logger.info(f'File upload initiated: {filename}')
    return jsonify({'message': 'File upload initiated'}), 202

def save_file(file_data, filename):
    try:
        # Save the file data to the specified path
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
            f.write(file_data.getbuffer())
        app.logger.info(f'File uploaded successfully: {filename}')
    except Exception as e:
        app.logger.error(f'Error saving file: {e}')

@app.route('/start-task', methods=['POST'])
def start_task():
    info = request.get_json()
    file_name = info['fileName']
    file_name = secure_filename(file_name)
    prompt = info.get('prompt', '')
    app.logger.info(f"start_task, prompt: {prompt}")
    task_id = str(uuid.uuid4())
    task_statuses[task_id] = 'PENDING'
    task_messages[task_id] = []
    threading.Thread(target=run_long_task, args=(task_id, file_name, prompt)).start()
    return jsonify({"task_id": task_id})

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    status = task_statuses.get(task_id, 'NOT FOUND')
    return jsonify({"task_id": task_id, "status": status})

@app.route('/task-latest-message/<task_id>', methods=['GET'])
def task_latest_message(task_id):
    with lock:
        messages = task_messages.get(task_id, [])
        if messages:
            return jsonify({"task_id": task_id, "message": messages[-1]})
        else:
            return jsonify({"task_id": task_id, "status": "no messages"}), 404
        
@app.route('/get-js-file/<filename>', methods=['GET'])
def get_js_file(filename):
    try:
        # Adjust the path to match where the JS file is saved
        filename = secure_filename(filename)
        folder_name = Path(filename)
        directory = Path(__file__).parent.joinpath('data', 'tree', folder_name.stem, 'json')
        json_folders = list(directory.iterdir())
        json_folders.sort()
        json_folder = json_folders[-1]
        
        with open(directory.joinpath(json_folder, 'data.json'), 'r') as f:
            data = json.load(f)
        app.logger.info(f"Send {filename} dictionary.")
        return jsonify({'dictionary': data})
    except Exception as e:
        app.logger.error(f"Error sending file: {e}")
        return jsonify({'error': 'File not found'}), 404

def run_long_task(task_id, filename, prompt):
    try:
        # Split the audio file
        split_audio_script = './scripts/split_audio.sh'
        command = ['bash', split_audio_script, filename]
        task_statuses[task_id] = 'RUNNING_SPLIT'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: RUNNING_SPLIT")
        app.logger.info(f"split_audio.py, status: {task_statuses[task_id]}")
        split_audio_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"split_audio.py, returncode: {split_audio_result.returncode}")

        if split_audio_result.returncode != 0:
            raise Exception(f"split_audio failed: {split_audio_result.stderr}")

        # Update status after splitting audio
        task_statuses[task_id] = 'SUCCESS_SPLIT'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: SUCCESS_SPLIT")
        app.logger.info(f"split_audio.py, status: {task_statuses[task_id]}")

        time.sleep(3)

        # Transcribe it to a text file
        transcribe_script = './scripts/transcribe.sh'
        command = ['bash', transcribe_script, filename, prompt]
        task_statuses[task_id] = 'RUNNING_TRANSCRIBE'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: RUNNING_TRANSCRIBE")
        app.logger.info(f"transcribe.py, status: {task_statuses[task_id]}")
        transcribe_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"transcribe.py, returncode: {transcribe_result.returncode}")

        if transcribe_result.returncode != 0:
            raise Exception(f"transcribe failed: {transcribe_result.stderr}")

        # time.sleep(10)
        # app.logger.info(f"transcribe.py, status: {task_statuses[task_id]}")

        # Update status after transcription
        task_statuses[task_id] = 'SUCCESS_TRANSCRIBE'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: SUCCESS_TRANSCRIBE")
        app.logger.info(f"transcribe.py, status: {task_statuses[task_id]}")

        time.sleep(3)

        # Summarize transcribed texts
        summarize_script = './scripts/summarize.sh'
        folder_name = Path(filename)
        model_name = 'gpt-4-1106-preview'
        command = ['bash', summarize_script, folder_name.stem, model_name]
        task_statuses[task_id] = 'RUNNING_SUMMARIZE'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: RUNNING_SUMMARIZE")
        app.logger.info(f"summarize.py, status: {task_statuses[task_id]}")
        summarize_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"summarize.py, returncode: {summarize_result.returncode}")
        
        # Update status after summarization
        task_statuses[task_id] = 'SUCCESS_SUMMARIZE'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: SUCCESS_SUMMARIZE")
        app.logger.info(f"summarize.py, status: {task_statuses[task_id]}")
        
        time.sleep(3)
        
        # Convert summarization into json
        convert_script = './scripts/conversion.sh'
        folder_name = Path(filename)
        model_name = 'gpt-4-1106-preview'
        command = ['bash', convert_script, folder_name.stem, model_name]
        task_statuses[task_id] = 'RUNNING_CONVERSION'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: RUNNING_CONVERSION")
        app.logger.info(f"conversion.py, status: {task_statuses[task_id]}")
        convert_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"conversion.py, returncode: {convert_result.returncode}")
        
        # Update status after conversion
        task_statuses[task_id] = 'SUCCESS_CONVERSION'
        with lock:
            task_messages[task_id].append(f"Task {task_id} status: SUCCESS_CONVERSION")
        app.logger.info(f"conversion.py, status: {task_statuses[task_id]}")
        
        time.sleep(3)

        # Final task completion
        task_statuses[task_id] = 'SUCCESS'
        with lock:
            task_messages[task_id].append(f"Task {task_id} completed successfully")

    except Exception as e:
        task_statuses[task_id] = 'FAILURE'
        with lock:
            task_messages[task_id].append(f"Task {task_id} failed with exception: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=False)
