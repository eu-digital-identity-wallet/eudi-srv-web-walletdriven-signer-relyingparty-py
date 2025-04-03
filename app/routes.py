# coding: latin-1
###############################################################################
# Copyright 2025 European Commission
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
import model.wallet.db as db

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

@rp.route('/document/options', methods=['POST'])
@login_required
def check():
    document_type_chosen = request.form["items"]
    app.logger.info(f"Document Types Selected: {document_type_chosen}.")

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
        return render_template('500.html', error="One of the types selected is not supported.")
    app.logger.info("Successfully retrieved the filename: "+ str(documents_chosen))

    hash_algos = [{"name":"SHA256", "oid":"2.16.840.1.101.3.4.2.1"}]
    return render_template('select-options-page.html', list_docs=list(zip(documents_chosen, signature_format)), digest_algorithms=hash_algos)

# Retrieve document with given name
@rp.route('/document/<path:filename>', methods=['GET'])
def serve_docs(filename):
    app.logger.info("Requested the file: "+ filename)
    return send_from_directory('docs', filename)

@rp.route("/document/sign", methods=['POST'])
@login_required
def sca_signature_flow():
    form = request.form
    app.logger.info("Received a form with signing options for the document "+form.get("filename"))

    form_global = session.get("form_global")
    if form_global is None:
        form_global = [form]
        update_session_values(variable_name="form_global", variable_value=form_global)
    else:
        form_global.append(form)
        update_session_values(variable_name="form_global", variable_value=form_global)

    app.logger.info("Successfully saved the options chosen.")
    return Response("Ok", 200)

@rp.route("/document/sign", methods=['GET'])
@login_required
def sca_signature_page():
    return render_template('select-wallet-page.html')

def get_document_content(filename):
    # Construct the path to the file in the "docs" folder
    file_path = os.path.join(Config.LOAD_FOLDER, filename)

    # Check if the file exists before trying to read it
    if not os.path.isfile(file_path):
        return f"File '{filename}' not found in the docs directory", 404

    # Read the content of the file to encode it in base64
    with open(file_path, 'rb') as document:
        document_content = document.read()
    return document_content

def start_wallet_interaction(wallet_url, scheme):
    list_forms = session.get("form_global")
    if list_forms is None:
        app.logger.error("The signature options information is missing.")
        render_template("500.html", error="The signature settings are missing.")

    documents_info = []
    documents_url = []
    hash_algorithm_oid = None

    for form in list_forms:
        filename = form.get("filename")
        hash_algorithm_oid = form.get("digest_algorithm")
        if filename is None:
            app.logger.error("The filename is missing.")
            render_template("500.html", error="One of the filenames is missing.")
        app.logger.info(f"Document to sign: {filename}. Hash Algorithm: {hash_algorithm_oid}")

        document_content = get_document_content(filename)
        documents_info.append({"filename": filename, "document_content": document_content})

        document_url = route_url+"/document/"+filename
        documents_url.append(document_url)

    link_to_wallet_tester, nonce = wallet_interaction.sd_retrieval_from_authorization_request(
        documents_info=documents_info,
        documents_url=documents_url,
        hash_algorithm_oid=hash_algorithm_oid,
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
@login_required
def sign_with_wallet():
    client_id_scheme = request.args.get("scheme")
    if client_id_scheme != "pre-registered" and client_id_scheme != "x509_san_dns":
        return render_template("500.html")
    app.logger.info("Client Id Scheme: " + client_id_scheme)

    wallet_url = "mdoc-openid4vp://" + Config.service_domain
    return start_wallet_interaction(wallet_url, client_id_scheme)


@rp.route("/document/sign/wallet/reference-implementation", methods=['GET'])
@login_required
def sign_with_reference_implementation():
    client_id_scheme = request.args.get("scheme")
    if client_id_scheme != "pre-registered" and client_id_scheme != "x509_san_dns":
        return render_template("500.html")
    app.logger.info("Client Id Scheme: " + client_id_scheme)

    wallet_url = "eudi-rqes://" + Config.service_domain
    return start_wallet_interaction(wallet_url, client_id_scheme)


@rp.route("/document/signed", methods=['GET'])
@login_required
def wait_for_signed_document():
    nonce = request.args.get('nonce')
    app.logger.info(f"Response URI where to retrieve signed document: {nonce}")
    timeout = time.time() + 60*10 # 10 minutes
    
    signed_document = None
    found = False 
    while not found and time.time() < timeout:
        response = wallet_interaction.retrieve_signed_objects(nonce=nonce)
        if response is not None:
            found = True
            signed_document = response
            app.logger.info(f"Retrieved signed document.")
        else:
            app.logger.info("Waiting for signed document...")
            time.sleep(15)
    
    if not found:
        db.remove_request_object_with_request_id(nonce)
        remove_session_values("form_global")
        return Response("Relying Party Tester timed out while waiting for the signed document from the Wallet.", status=408)
    else:
        form_list = session.get("form_global")
        data = []
        for form, doc in zip(form_list, signed_document):
            filename = form.get("filename")
            app.logger.info(f"Found the filename to sign {filename} and expected signed document.")

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
