# coding: latin-1
###############################################################################
# Copyright 2024 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

import os, base64, qrcode, io, requests, mimetypes, time, json, time
from flask import (
    Blueprint, render_template, request, session, send_from_directory, current_app as app
)
from flask_login import login_required
from app_config.config import ConfService as cfgserv
import app.wallet_interactions.requests as wallet_interaction

rp = Blueprint("RP", __name__, url_prefix="/rp/tester")
rp.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

DIGEST_OIDS = {
    "md5": "1.2.840.113549.2.5",
    "sha1": "1.3.14.3.2.26",
    "sha224": "2.16.840.1.101.3.4.2.4",
    "sha256": "2.16.840.1.101.3.4.2.1",
    "sha384": "2.16.840.1.101.3.4.2.2",
    "sha512": "2.16.840.1.101.3.4.2.3",
    "sha3_224": "2.16.840.1.101.3.4.2.7",
    "sha3_256": "2.16.840.1.101.3.4.2.8",
    "sha3_384": "2.16.840.1.101.3.4.2.9",
    "sha3_512": "2.16.840.1.101.3.4.2.10",
}

route_url = cfgserv.service_url+"/tester"

@rp.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@rp.route('/document/select', methods=['GET'])
@login_required
def select_document():
    return render_template('select_document.html')

def get_signature_format(filename):
    if filename.endswith('.pdf'):
        return 'PAdES'
    elif filename.endswith('.xml'):
        return 'XAdES'
    elif filename.endswith('.json'):
        return 'JAdES'
    else:
        return 'CAdES'

# Present page with signing options
@rp.route('/document/options', methods=['GET'])
@login_required
def check():
    document_type = request.args.get('document')
    if document_type == 'pdf':
        filename = 'sample.pdf'
    elif document_type == 'json':
        filename = 'sample.json'
    elif document_type == 'txt':
        filename = 'sample.txt'
    elif document_type == 'xml':
        filename = 'sample.xml'
    else:
        return "Invalid document type selected."    
    
    signature_format = get_signature_format(filename)

    hash_algos = [{"name":"SHA256", "oid":"2.16.840.1.101.3.4.2.1"}]
        
    return render_template('select_options.html', filename=filename, signature_format=signature_format, digest_algorithms=hash_algos)

# Retrieve document with given name
@rp.route('/document/<path:filename>')
def serve_docs(filename):
    return send_from_directory('docs', filename)

def get_base64_document(filename):
    # Construct the path to the file in the "docs" folder
    file_path = os.path.join(cfgserv.LOAD_FOLDER, filename)

    # Check if the file exists before trying to read it
    if not os.path.isfile(file_path):
        return f"File '{filename}' not found in the docs directory", 404
    
    # Read the content of the file to encode it in base64
    base64_document = None
    with open(file_path, 'rb') as document:
        base64_document = base64.b64encode(document.read()).decode("utf-8")
    
    return base64_document

@rp.route("/document/sign", methods=['POST'])
def sca_signature_flow():
    form_local= request.form
    update_session_values(variable_name="form_global", variable_value=form_local)

    filename = form_local["filename"]
    if not filename:
        return "Filename is required", 400  # Return an error if filename is None
    app.logger.info(f"Retrieved document to sign: {filename}")

    base64_document = get_base64_document(filename)
    hash_algorithm_oid = form_local["digest_algorithm"]        

    document_url = route_url+"/document/"+filename
    app.logger.info(f"Retrieve Document URL: {document_url}")
    
    link_to_wallet_tester, response_uri = wallet_interaction.sd_retrieval_from_authorization_request(
        document=base64_document,
        filename=filename,
        document_url=document_url,
        hashAlgorithmOID=hash_algorithm_oid
    )    
    app.logger.info(f"Link to Wallet Tester: {link_to_wallet_tester} & Response URI: {response_uri}")
    
    retrieve_signed_document_url = route_url+"/document/signed?response_uri="+response_uri
    app.logger.info(f"URL where to retrieve signed document: {retrieve_signed_document_url}")
    
    # Render HTML page with QrCode
    qr_img = qrcode.make(link_to_wallet_tester)
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_img_base64 = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    return render_template('redirect_wallet.html', url=link_to_wallet_tester, qrcode=qr_img_base64, retrieve_signed_document_url=retrieve_signed_document_url)

@rp.route("/document/signed", methods=['GET'])
def wait_for_signed_document():
    response_uri = request.args.get('response_uri')
    app.logger.info(f"Response URI where to retrieve signed document: {response_uri}")
    
    timeout = time.time() + 60*2 # 2 minutes
    
    signed_document = None
    found = False 
    while not found and time.time() < timeout:
        response = requests.get(response_uri)
        if response.status_code == 200 and response.text != "None":
            found = True
            signed_document = response.text
            app.logger.info(f"Retrieved signed document.")
        elif response.status_code != 200:
            return "Error retrieving signed document", 500
        else:
            app.logger.info("Waiting for signed document...")
            time.sleep(15) # waits 15 seconds before trying again
    
    form_local = session["form_global"]

    filename = form_local["filename"]
    if not filename:
        return "Filename is required", 400 # Return an error if filename is None
    app.logger.info(f"Retrieved document to sign: {filename}")
          
    new_name = add_suffix_to_filename(os.path.basename(filename))
    mime_type, _ = mimetypes.guess_type(filename)
    
    return json.dumps({
        'document_signed_value': signed_document,
        'document_content_type': mime_type,
        'document_filename': new_name  
        })
    

def add_suffix_to_filename(filename, suffix="_signed"):
    name, ext = os.path.splitext(filename)
    return f"{name}{suffix}{ext}"

def update_session_values(variable_name, variable_value):
    if(session.get(variable_name) is not None):
        session.pop(variable_name)
    session[variable_name] = variable_value
