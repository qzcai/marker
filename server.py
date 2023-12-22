import os
import requests
import socket
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify
from urllib.parse import urlparse

from marker.convert import convert_single_pdf
from marker.logger import configure_logging
from marker.models import load_all_models

configure_logging()
app = Flask(__name__)
start_time = datetime.now()


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    file_path = data.get('file_path')
    max_pages = data.get('max_pages')
    parallel_factor = data.get('parallel_factor', 1)

    # Check if it's a local file
    file_name = None
    need_delete = False
    match is_local_or_url(file_path):
        case 'local':
            file_name = file_path

        case 'url':
            need_delete = True
            file_name = download_file(file_path)
            if file_name is None:
                return jsonify({'error': f'Error downloading {file_path}'}), 500

        case 'unknown':
            return jsonify({'error': f'Unknown file path {file_path}'}), 500

    full_text, out_meta = convert_single_pdf(file_name, model_lst, max_pages=max_pages, parallel_factor=parallel_factor)
    if need_delete:
        os.remove(file_name)

    return jsonify({'full_text': full_text, 'out_meta': out_meta})


def is_local_or_url(file_path):
    # Check if it's a local file
    if os.path.isfile(file_path):
        return 'local'
    # Check if it's a valid URL
    elif urlparse(file_path).scheme in ['http', 'https']:
        return 'url'
    else:
        return 'unknown'


def download_file(url):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        # Write the contents of the response to the file
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                temp_file.write(chunk)

        # Return the path to the temporary file
        return temp_file.name
    else:
        return None


@app.route('/health', methods=['GET'])
def health():
    uptime = datetime.now() - start_time
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return jsonify({'uptime': str(uptime), 'host': host_name, 'ip': host_ip})


if __name__ == "__main__":
    model_lst = load_all_models()
    app.run()
