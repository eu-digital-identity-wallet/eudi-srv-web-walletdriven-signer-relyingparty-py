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

import os, base64, qrcode, io, mimetypes, json, time
from flask import (
    Blueprint, render_template, request, session, send_from_directory, current_app as app, Response
)
from flask_login import login_required
from app_config.config import ConfigClass as Config
import model.wallet.requests as wallet_interaction

rp = Blueprint("RP", __name__, url_prefix="/rp/tester")
rp.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

route_url = Config.service_url + "/tester"

@rp.route('/', methods=['GET'])
def main():
    return render_template('welcome-page.html')

@rp.route('/document/select', methods=['GET'])
@login_required
def select_document():
    return render_template('select-document-page.html')

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
        app.logger.error("The document type selected is not supported.")
        return render_template('500.html', error="The type of the document selected is not supported.")
    app.logger.info("Sucessfully retrieved the filename.")
    
    signature_format = get_signature_format(filename)
    app.logger.info("Successfully retrieved the signature format: "+signature_format)

    hash_algos = [{"name":"SHA256", "oid":"2.16.840.1.101.3.4.2.1"}]
        
    return render_template('select-options-page.html', filename=filename, signature_format=signature_format, digest_algorithms=hash_algos)

# Retrieve document with given name
@rp.route('/document/<path:filename>', methods=['GET'])
def serve_docs(filename):
    return send_from_directory('docs', filename)

@rp.route("/document/sign", methods=['POST'])
@login_required
def sca_signature_flow():
    form_local = request.form
    update_session_values(variable_name="form_global", variable_value=form_local)
    app.logger.info("Successfully saved the options chosen.")
    return render_template('select-wallet-page.html')

def get_base64_document(filename):
    # Construct the path to the file in the "docs" folder
    file_path = os.path.join(Config.LOAD_FOLDER, filename)

    # Check if the file exists before trying to read it
    if not os.path.isfile(file_path):
        return f"File '{filename}' not found in the docs directory", 404

    # Read the content of the file to encode it in base64
    with open(file_path, 'rb') as document:
        base64_document = base64.b64encode(document.read()).decode("utf-8")

    return base64_document

def start_wallet_interaction(wallet_url):
    form_local = session.get("form_global")
    if form_local is None:
        app.logger.error("The Signature Options Form is missing.")
        render_template("500.html", error="The signature settings are missing.")
    
    filename = form_local["filename"]
    if filename is None:
        app.logger.error("The filename is missing.")
        render_template("500.html", error="Filename is missing.")
    app.logger.info(f"Retrieved document to sign: {filename}")
    
    base64_document = get_base64_document(filename)
    hash_algorithm_oid = form_local["digest_algorithm"]
    app.logger.info("Hash Algorithm: "+hash_algorithm_oid)   
      
    document_url = route_url+"/document/"+filename
    app.logger.info(f"Retrieve Document URL: {document_url}")
    
    link_to_wallet_tester, nonce = wallet_interaction.sd_retrieval_from_authorization_request(
        document=base64_document,
        filename=filename,
        document_url=document_url,
        hash_algorithm_oid=hash_algorithm_oid,
        response_type="sign_response",
        wallet_url=wallet_url
    )    
    app.logger.info(f"Link to Wallet Tester: {link_to_wallet_tester} & Response URI: {nonce}")
    
    retrieve_signed_document_url = route_url+"/document/signed?nonce="+nonce
    app.logger.info(f"URL where to retrieve signed document: {retrieve_signed_document_url}")
    
    # Render HTML page with QrCode
    qr_img = qrcode.make(link_to_wallet_tester)
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_img_base64 = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    return render_template('redirect-wallet-page.html', url=link_to_wallet_tester, qrcode=qr_img_base64, retrieve_signed_document_url=retrieve_signed_document_url)

@rp.route("/document/sign/tester", methods=['GET'])
@login_required
def sign_with_wallet_tester():
    wallet_url = Config.wallet_url
    return start_wallet_interaction(wallet_url)

@rp.route("/document/sign/wallet", methods=['GET'])
def sign_with_wallet(): 
    wallet_url = "mdoc-openid4vp://" + Config.service_url
    return start_wallet_interaction(wallet_url)
    
@rp.route("/document/signed", methods=['GET'])
def wait_for_signed_document():
    nonce = request.args.get('nonce')
    app.logger.info(f"Response URI where to retrieve signed document: {nonce}")
    
    timeout = time.time() + 60*10 # 2 minutes
    
    signed_document = None
    found = False 
    while not found and time.time() < timeout:
        response = wallet_interaction.retrieve_signed_objects(nonce=nonce)
        print(response)
        if response is not None:
            found = True
            signed_document = response
            app.logger.info(f"Retrieved signed document.")
        else:
            app.logger.info("Waiting for signed document...")
            time.sleep(15) # waits 15 seconds before trying again
    
    if not found:
        return Response("Relying Party Tester timed out while waiting for the signed document from the Wallet.", status=408)
        
    else:
        form_local = session.get("form_global")
        filename = form_local["filename"]
        if not filename:
            return "Filename is required", 400  # Return an error if filename is None
        app.logger.info(f"Retrieved document to sign: {filename}")

        data = []
        for doc in signed_document:
            print(doc)
            new_name = add_suffix_to_filename(os.path.basename(filename))
            mime_type, _ = mimetypes.guess_type(filename)
            info = {
                'document_signed_value': doc,
                'document_content_type': mime_type,
                'document_filename': new_name
            }
            data.append(info)
        return json.dumps(data)

def add_suffix_to_filename(filename, suffix="_signed"):
    name, ext = os.path.splitext(filename)
    return f"{name}{suffix}{ext}"

def update_session_values(variable_name, variable_value):
    remove_session_values(variable_name)
    session[variable_name] = variable_value

def remove_session_values(variable_name):
    if session.get(variable_name) is not None:
        session.pop(variable_name)