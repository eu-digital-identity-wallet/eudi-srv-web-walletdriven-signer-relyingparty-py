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

import os, base64, qrcode, io, mimetypes, time
from flask import (
    Blueprint, render_template, request, session, send_from_directory, current_app as app, Response, jsonify
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
    remove_session_values(variable_name="form_global")
    return render_template('select-document-page.html')

# Present page with signing options
@rp.route('/document/options', methods=['POST'])
@login_required
def check():
    document_type_chosen = request.form["items"]
    app.logger.info("The document type chosen to sign is: "+document_type_chosen)

    documents_chosen = []
    signature_format = []
    if 'pdf' in document_type_chosen:
        documents_chosen.append('sample.pdf')
        signature_format.append('PAdES')
    if 'json' in document_type_chosen:
        documents_chosen.append('sample.json')
        signature_format.append('JAdES')
    if 'txt' in document_type_chosen:
        documents_chosen.append('sample.txt')
        signature_format.append('CAdES')
    if 'xml' in document_type_chosen:
        documents_chosen.append('sample.xml')
        signature_format.append('XAdES')
    if 'pdf' not in document_type_chosen and 'json' not in document_type_chosen and 'txt' not in document_type_chosen and 'xml' not in document_type_chosen:
        app.logger.error("The document type selected is not supported.")
        return render_template('500.html', error="The type of the document selected is not supported.")
    app.logger.info("Successfully retrieved the filename.")
    
    app.logger.info("Successfully retrieved the signature format.")

    hash_algos = [{"name":"SHA256", "oid":"2.16.840.1.101.3.4.2.1"}]

    return render_template('select-options-page.html', list_docs=list(zip(documents_chosen, signature_format)), digest_algorithms=hash_algos)

# Retrieve document with given name
@rp.route('/document/<path:filename>', methods=['GET'])
def serve_docs(filename):
    return send_from_directory('docs', filename)

@rp.route("/document/sign", methods=['POST'])
@login_required
def sca_signature_flow():
    form_local = request.form
    print(form_local)

    form_global = session.get("form_global")
    if form_global is None:
        form_global = [form_local]
        update_session_values(variable_name="form_global", variable_value=form_global)
    else:
        form_global.append(form_local)
        update_session_values(variable_name="form_global", variable_value=form_global)
    print(session.get("form_global"))

    app.logger.info("Successfully saved the options chosen.")
    return Response("Ok", 200)

@rp.route("/document/sign", methods=['GET'])
@login_required
def sca_signature_page():
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

@rp.route("/document/sign/scheme")
@login_required
def select_client_id_scheme():
    return render_template("select-scheme-options.html")


def start_wallet_interaction(wallet_url, scheme):
    form_list = session.get("form_global")
    if form_list is None:
        app.logger.error("The Signature Options Form is missing.")
        render_template("500.html", error="The signature settings are missing.")

    print(len(form_list))

    documents_info = []
    documents_url = []
    hash_algorithm_oid = None

    for form in form_list:
        filename = form["filename"]
        if filename is None:
            app.logger.error("The filename is missing.")
            render_template("500.html", error="Filename is missing.")
        app.logger.info(f"Retrieved document to sign: {filename}")
    
        base64_document = get_base64_document(filename)
        documents_info.append({"filename": filename, "document_base64": base64_document})

        hash_algorithm_oid = form["digest_algorithm"]
        app.logger.info("Hash Algorithm: "+hash_algorithm_oid)
      
        document_url = route_url+"/document/"+filename
        documents_url.append(document_url)
        app.logger.info(f"Retrieve Document URL: {document_url}")


    link_to_wallet_tester, nonce = wallet_interaction.sd_retrieval_from_authorization_request(
        documents_info = documents_info,
        documents_url=documents_url,
        hash_algorithm_oid=hash_algorithm_oid,
        response_type="sign_response",
        wallet_url=wallet_url,
        client_id_scheme = scheme
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
    client_id_scheme = request.args.get("scheme")
    if client_id_scheme != "pre-registered" and client_id_scheme != "x509_san_dns":
        return render_template("500.html")
    app.logger.info("Client Id Scheme: "+client_id_scheme)

    wallet_url = Config.wallet_url
    return start_wallet_interaction(wallet_url, client_id_scheme)

@rp.route("/document/sign/wallet", methods=['GET'])
def sign_with_wallet():
    client_id_scheme = request.args.get("scheme")
    if client_id_scheme != "pre-registered" and client_id_scheme != "x509_san_dns":
        return render_template("500.html")
    app.logger.info("Client Id Scheme: " + client_id_scheme)

    wallet_url = "mdoc-openid4vp://" + Config.service_url
    return start_wallet_interaction(wallet_url, client_id_scheme)
    
@rp.route("/document/signed", methods=['GET'])
def wait_for_signed_document():
    nonce = request.args.get('nonce')
    app.logger.info(f"Response URI where to retrieve signed document: {nonce}")
    
    timeout = time.time() + 60*10 # 10 minutes
    
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
            time.sleep(15)
    
    if not found:
        remove_session_values("form_global")
        return Response("Relying Party Tester timed out while waiting for the signed document from the Wallet.", status=408)
        
    else:
        form_list = session.get("form_global")
        data = []

        for form, doc in zip(form_list, signed_document):
            filename = form["filename"]
            if not filename:
                return "Filename is required", 400  # Return an error if filename is None
            app.logger.info(f"Retrieved document to sign: {filename}")

            print(doc)
            new_name = add_suffix_to_filename(os.path.basename(filename))
            mime_type, _ = mimetypes.guess_type(filename)
            info = {
                'document_signed_value': doc,
                'document_content_type': mime_type,
                'document_filename': new_name
            }
            data.append(info)

        remove_session_values("form_global")

        return jsonify(data)

def add_suffix_to_filename(filename, suffix="_signed"):
    name, ext = os.path.splitext(filename)
    return f"{name}{suffix}{ext}"

def update_session_values(variable_name, variable_value):
    remove_session_values(variable_name)
    session[variable_name] = variable_value

def remove_session_values(variable_name):
    if session.get(variable_name) is not None:
        session.pop(variable_name)