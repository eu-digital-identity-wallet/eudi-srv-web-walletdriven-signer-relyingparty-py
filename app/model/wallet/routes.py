import os
from flask import (
    Blueprint, request, current_app as app, jsonify
)
from model.wallet import db

wallet = Blueprint("wallet", __name__, url_prefix="/rp/wallet")
wallet.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@wallet.route('/sd/<string:nonce>', methods=['GET'])
def retrieve_signer_document(nonce):
    app.logger.info("'Request Object' requested by the client id: "+nonce)
    request_object = db.get_request_object_from_db(nonce)
    app.logger.info("Retrieved the request object.")
    return request_object, 200

# endpoint to receive the signed document
@wallet.route('/sd/upload/<string:nonce>', methods=['POST'])
def place_signed_document(nonce):
    app.logger.info("Uploading Signed Data Object.")
    json_data = request.form
    if not json_data:
        app.logger.error("Error retrieving Form Data.")
        return jsonify({"error": "Invalid request format"}), 400

    error = json_data.get("error")
    state = json_data.get("state")

    document_with_signature = json_data.getlist("documentWithSignature")
    print(len(document_with_signature))
        #document_with_signature = json_data.getlist("documentWithSignature[]")
        #print(document_with_signature)
        #print(len(document_with_signature))
    if document_with_signature is not None:
        app.logger.info("DocumentWithSignature in request.")
        print(len(document_with_signature))

        for doc in document_with_signature:
            print(doc)
            db.add_to_signed_data_object_table(nonce, doc, error)
            app.logger.info("Saved Signed Document.")
        app.logger.info("Uploaded Signed Document.")
        return "OK", 200
        
    signature_object = json_data.getlist("signatureObject")
    if signature_object is not None:
        app.logger.info("SignatureObject in request.")
        for sig in signature_object:
            db.add_to_signed_data_object_table(nonce, sig, error)
        app.logger.info("Uploaded Signed Document.")
        return "OK", 200
            
    if signature_object is None and document_with_signature is None:
        if error is None:
            error = "Signature Failed."
        # save to database a request associated to client_id
        db.add_to_signed_data_object_table(nonce, None, error)
        app.logger.info("Uploaded Signed Document.")
        raise ValueError("Receiving signed document failed.")