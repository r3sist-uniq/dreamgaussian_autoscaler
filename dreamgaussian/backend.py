import requests
from flask import jsonify, abort
from backend import GenericBackend
from dreamgaussian.metrics import Metrics  # Adjust the import path as needed

INSTANCE_ID = "localhost"
INSTANCE_PORT = '5000'
MODEL_SERVER = f"http://{INSTANCE_ID}:{INSTANCE_PORT}"

class Backend(GenericBackend):
    def __init__(self, container_id, control_server_url, master_token, send_data):
        metrics = Metrics(id=container_id, master_token=master_token, control_server_url=control_server_url, send_server_data=send_data)
        super().__init__(master_token=master_token, metrics=metrics)
        self.model_server_addr = MODEL_SERVER

    def generate_3d_model(self, request_data):
        endpoint = "/inference_with_image" 
        image_data = request_data

        def response_func(response):
            try:
                return response.json()  
            except ValueError:
                print(f"[Backend] JSONDecodeError for response: {response.text}")
                return None 

        status_code, result, time_elapsed = super().generate(image_data, self.model_server_addr, endpoint, response_func, metrics=True)
        
        if status_code == 200 and result is not None:
            return jsonify(result), 200 
        else:
            return jsonify({"error": "Failed to generate 3D model"}), status_code if result is not None else 500
    
######################################### FLASK HANDLER METHODS ###############################################################
        
    def generate_3d_model_handler(self, request):
        try:
            # model_dict could be wrong here (sd example)
            auth_dict, model_dict = self.format_request(request.json)
            if auth_dict and not self.check_signature(**auth_dict):
                abort(401, description="Unauthorized request")

            payload = request.json
            if not payload:
                abort(400, description="Invalid request data")

            response, status_code = self.generate_3d_model(payload)
            return response, status_code
        except Exception as e:
            print(f"Error processing 3D model generation request: {e}")
            abort(500, description="Internal server error")

    flask_dict = {
        "POST": {
            "/generate_3d_model": generate_3d_model_handler,
        }
    }
