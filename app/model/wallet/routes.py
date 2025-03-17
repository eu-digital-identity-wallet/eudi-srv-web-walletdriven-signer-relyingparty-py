import os
import textwrap
from flask import (Blueprint, request, current_app as app, jsonify)
from model.wallet import db

wallet = Blueprint("wallet", __name__, url_prefix="/rp/wallet")
wallet.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

# Endpoint that allows to retrieve the Request Object (Signer's Document)
@wallet.route('/sd/<string:nonce>', methods=['GET'])
def retrieve_request_object(nonce):
    app.logger.info(f"Retrieving 'Request Object' of the Request {nonce}.")
    try:
        request_object = db.get_request_object_from_db(nonce)
        app.logger.info("Retrieved the Request Object and removed it from the database.")
    except ValueError as e:
        app.logger.error(f"An error was caught while trying to save the Request Object to the Database: {e}.")
        return None, 404

    return request_object, 200

# Endpoint that allows to save signed documents as a response to signature request
@wallet.route('/sd/upload/<string:nonce>', methods=['POST'])
def place_signed_document(nonce):
    app.logger.info(f"Uploading Signed Data Object for the Request {nonce}.")
    form = request.form

    if not form:
        app.logger.error("Error retrieving Signed Data Object: expected to received the signed document as a form.")
        return jsonify({"error": "Invalid request format"}), 400

    error = form.get("error")
    app.logger.error(error)
    state = form.get("state")
    app.logger.info(state)

    if not db.exists_request_object_with_request_id(nonce):
        return f"The application has no record of a request associated to {nonce}", 400

    signed_data_objects = []

    document_with_signature = retrieve_list_values_from_form_urlencoded(form, "documentWithSignature")
    docs_signed_short_debug = textwrap.shorten(str(document_with_signature), width=50, placeholder="...")
    app.logger.info(f"Retrieved the 'document_with_signature': {docs_signed_short_debug}")
    if document_with_signature is not None:
        app.logger.info("Successfully retrieved 'documentWithSignature'.")
        app.logger.info(f"Retrieved {len(document_with_signature)} signed documents.")
        for doc in document_with_signature:
            app.logger.info(doc)
            signed_data_objects.append(doc)
        app.logger.info("Successfully uploaded all the signed documents.")

    signature_object = retrieve_list_values_from_form_urlencoded(form, "signatureObject")
    signature_short_debug = textwrap.shorten(str(signature_object), width=50, placeholder="...")
    app.logger.info(f"Retrieved the 'signature_object': {signature_short_debug}")
    if signature_object is not None:
        app.logger.info("Successfully retrieved 'signatureObject'.")
        app.logger.info(f"Retrieved {len(signature_object)} signed documents.")
        for signature in signature_object:
            app.logger.info(signature)
            signed_data_objects.append(signature)
        app.logger.info("Successfully uploaded all the signed document.")

    if signature_object is None and document_with_signature is None:
        if error is None:
            error = "Upload of the Signed Data Objects failed."
        db.add_to_signed_data_object_table(nonce, None, error)
        return "It was impossible to upload the signed data objects.", 400

    try:
        db.add_to_signed_data_object_table(nonce, signed_data_objects, error)
        db.remove_request_object_with_request_id(nonce)
        return "OK", 200
    except ValueError as e:
        app.logger.error(f"An error was caught while trying to save the signed data objects to the database: {e}.")
        return "It was impossible to upload the signed data objects.", 400

def retrieve_list_values_from_form_urlencoded(form, variable_name):
    # Indexed array (e.g., var[0]=_&var[1]=_) or Bracket notation (e.g., var[]=_&var[]=_)
    variable_list = [v for k, v in form.items() if k.startswith(variable_name+'[')]
    if variable_list:
        app.logger.info("Variable "+variable_name+" received through indexed list (e.g., 'var[0]=_&var[1]=_' or 'var[]=_&var[]=_').")
        app.logger.debug(variable_list)
        return variable_list

    # Repeated keys (e.g., var=_&var=_) or Comma-separated values (e.g., var=_,_) or URLEncoded List (e.g., var=%5B_,_%5D)
    variable_list = form.getlist(variable_name)
    if variable_list:
        app.logger.info("Variable " + variable_name + " received through repeated keys (e.g., var=_&var=_ or (e.g., var=_,_) or var=%5B_,_%5D).")
        app.logger.debug(variable_list)
        processed_list = []
        for elem in variable_list:
            elem = elem.strip()
            if elem.startswith("[") and elem.endswith("]"):
                try:
                    elem = eval(elem)
                    if isinstance(elem, list):
                        processed_list.extend(elem)
                    else:
                        processed_list.append(str(elem))
                except Exception:
                    processed_list.append(elem) # Fallback: keep original string
            else:
                processed_list.append(elem)
        app.logger.info(f"Processed List Len: {len(processed_list)}")

        # Comma-separated values (e.g., var=_,_)
        csv_list = []
        for item in processed_list:
            csv_list.extend(item.split(','))
        if csv_list:
            app.logger.info("Variable " + variable_name + " received through comma-separated values.")
            app.logger.debug(f"CSC List Len: {len(csv_list)}")
            return csv_list
        return processed_list

    # None of the above
    return None