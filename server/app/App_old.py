import os
import time
import logging
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from queue import Queue, Empty
import threading
import io
import uuid

app = Flask(__name__)
CORS(app)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# In-memory message queues
message_queues = {}
task_statuses = {}

# Lock for thread-safe operations
lock = threading.Lock()

# Message Broker Class
class MessageBroker:
    def __init__(self):
        self.queues = {}
    
    def create_queue(self, queue_name):
        with lock:
            if queue_name not in self.queues:
                self.queues[queue_name] = Queue()
                app.logger.info(f'Queue created: {queue_name}')
    
    def produce(self, queue_name, message):
        with lock:
            if queue_name in self.queues:
                self.queues[queue_name].put(message)
                app.logger.info(f'Message produced in queue {queue_name}: {message}')
    
    def consume(self, queue_name):
        with lock:
            if queue_name in self.queues:
                try:
                    message = self.queues[queue_name].get_nowait()
                    app.logger.info(f'Message consumed from queue {queue_name}: {message}')
                    return message
                except Empty:
                    app.logger.info(f'No messages in queue {queue_name}')
                    return None
        return None

# Initialize Message Broker
broker = MessageBroker()

@app.route('/create_queue', methods=['POST'])
def create_queue():
    data = request.json
    queue_name = data['queue_name']
    broker.create_queue(queue_name)
    return jsonify({"status": "queue created"})

@app.route('/produce', methods=['POST'])
def produce_message():
    data = request.json
    queue_name = data['queue_name']
    message = data['message']
    broker.produce(queue_name, message)
    return jsonify({"status": "message produced"})

@app.route('/consume', methods=['GET'])
def consume_message():
    queue_name = request.args.get('queue_name')
    message = broker.consume(queue_name)
    if message:
        return jsonify({"message": message})
    else:
        return jsonify({"status": "no messages"}), 404

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
    app.logger.info(f'File upload initiated: {file.filename}')
    return jsonify({'message': 'File upload initiated'}), 202

def save_file(file_data, filename):
    try:
        # Save the file data to the specified path
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
            f.write(file_data.getbuffer())
        app.logger.info(f'File uploaded successfully: {filename}')
        # After saving, you can push a message to the message broker if needed
        broker.produce('file_uploads', f'File {filename} uploaded successfully')
    except Exception as e:
        app.logger.error(f'Error saving file: {e}')
        broker.produce('file_uploads', f'Error uploading file {filename}')

@app.route('/start-task', methods=['POST'])
def start_task():
    info = request.get_json()
    file_name = info['fileName']
    prompt = info.get('prompt', '')
    task_id = str(uuid.uuid4())
    task_statuses[task_id] = 'PENDING'
    threading.Thread(target=run_long_task, args=(task_id, file_name, prompt)).start()
    return jsonify({"task_id": task_id})

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    status = task_statuses.get(task_id, 'NOT FOUND')
    return jsonify({"task_id": task_id, "status": status})

@app.route('/task-latest-message/<task_id>', methods=['GET'])
def task_latest_message(task_id):
    message = broker.consume('tasks')
    app.logger.info(f"task_latest_message, message: {message}")
    if message and task_id in message:
        return jsonify({"task_id": task_id, "message": message})
    else:
        return jsonify({"task_id": task_id, "status": "no messages"}), 404

def run_long_task(task_id, filename, prompt):
    try:
        # Split the audio file
        split_audio_script = './scripts/split_audio.sh'
        command = ['bash', split_audio_script, filename]
        task_statuses[task_id] = 'RUNNING_SPLIT'
        broker.produce('tasks', f"Task {task_id} status: RUNNING_SPLIT")
        app.logger.info(f"split_audio.py, status: {task_statuses[task_id]}")
        split_audio_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"split_audio.py, returncode: {split_audio_result.returncode}")
        
        if split_audio_result.returncode != 0:
            raise Exception(f"split_audio failed: {split_audio_result.stderr}")
        
        # Update status after splitting audio
        task_statuses[task_id] = 'SUCCESS_SPLIT'
        broker.produce('tasks', f"Task {task_id} status: SUCCESS_SPLIT")
        app.logger.info(f"split_audio.py, status: {task_statuses[task_id]}")
        
        time.sleep(2)
        
        # Transcribe it to a text file
        transcribe_script = './scripts/transcribe.sh'
        command = ['bash', transcribe_script, filename, prompt]
        task_statuses[task_id] = 'RUNNING_TRANSCRIBE'
        broker.produce('tasks', f"Task {task_id} status: RUNNING_TRANSCRIBE")
        app.logger.info(f"transcribe.py, status: {task_statuses[task_id]}")
        transcribe_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"transcribe.py, returncode: {transcribe_result.returncode}")
        
        if transcribe_result.returncode != 0:
            raise Exception(f"transcribe failed: {transcribe_result.stderr}")
        
        # time.sleep(10)
        # app.logger.info(f"transcribe.py, test")
        
        # Update status after transcription
        task_statuses[task_id] = 'SUCCESS_TRANSCRIBE'
        broker.produce('tasks', f'Task {task_id} status: SUCCESS_TRANSCRIBE')
        app.logger.info(f"transcribe.py, status: {task_statuses[task_id]}")
        
        time.sleep(2)
        
        # Final task completion
        task_statuses[task_id] = 'SUCCESS'
        broker.produce('tasks', f'Task {task_id} completed successfully')
        
        # script_path = './scripts/transcribe.sh'
        # command = ['bash', script_path, filename]
        # task_statuses[task_id] = 'RUNNING'
        # app.logger.info(f"run_long_task, status: {task_statuses[task_id]}")
        # result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # app.logger.info(f"result returncode: {result.returncode}")
        # if result.returncode == 0:
        #     task_statuses[task_id] = 'SUCCESS'
        #     broker.produce('tasks', f'Task {task_id} completed successfully')
        # else:
        #     task_statuses[task_id] = 'FAILURE'
        #     broker.produce('tasks', f'Task {task_id} failed with error: {result.stderr}')
    except Exception as e:
        task_statuses[task_id] = 'FAILURE'
        broker.produce('tasks', f'Task {task_id} failed with exception: {str(e)}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=False)
