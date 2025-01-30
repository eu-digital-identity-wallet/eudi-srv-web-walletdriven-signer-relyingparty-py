import os
from flask import (
    Blueprint, request, current_app as app
)
from app_config.config import ConfService as cfgserv
import app.wallet_interactions.db as db


wallet = Blueprint("wallet", __name__, url_prefix="/rp/wallet")
wallet.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@wallet.route('/sd/<string:client_id>', methods=['GET'])
def retrieveSignerDocument(client_id):   
    app.logger.info("'Request Object' requested by the client id: "+client_id)
    request_object = db.get_request_object_from_db(client_id)
    app.logger.info("Retrieved the request object.")
    return request_object, 200

# endpoint to receive the signed document
@wallet.route('/sd/upload/<string:client_id>', methods=['POST', 'GET'])
def placeSignedDocument(client_id):
    
    # Retrieve Signed Document
    if(request.method == 'GET'):
        signed_doc = db.get_signed_data_object_from_db(client_id)

        if(signed_doc is None):
            return "None", 200
        return signed_doc, 200
            
    
    # Handle POST request
    # Saves the signed document to the database        
    else:
        json_data = request.get_json(silent=True)
        documentWithSignature = json_data.get("documentWithSignature")
        if not documentWithSignature:
            return "Invalid JSON data", 400       

        # save to database a request associated to client_id
        db.add_to_signed_data_object_table(client_id, documentWithSignature)
        
        return "OK", 200
