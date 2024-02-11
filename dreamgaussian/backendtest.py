import requests
from flask import Response, send_file, abort, jsonify
import json
from backend import GenericBackend
from datetime import datetime
from dreamgaussian.metric import Metrics  # Adjust the import path as needed


INSTANCE_ID = "localhost"
INSTANCE_PORT = '5000'
MODEL_SERVER = INSTANCE_ID + ":" + INSTANCE_PORT


class Backend(GenericBackend):
    def __init__(self, container_id, control_server_url, master_token, send_data):
        metrics = Metrics(id=container_id, master_token=master_token, control_server_url=control_server_url, send_server_data=send_data)
        super().__init__(master_token=master_token, metrics=metrics)
        self.model_server_addr = MODEL_SERVER

    def generate_3d_model(self, image_data):
        start_time = datetime.now()
        try :
            response = requests.post(f"{self.model_server_addr}/generate_3d", json=image_data)
            if response.status_code == 200:
                self.metrics.start_req(image_data)
                glb_url = response.json().get('glb_url')
                self.metrics.finish_req(image_data, (datetime.now() - start_time).total_seconds())
                return jsonify({"glb_url": glb_url}), 200
            else:
                self.metrics.error_req(image_data)
                return jsonify({"error": "Error generating 3D model", "details": response.text}), response.status_code
        except requests.exceptions.RequestException as e:
            self.metrics.error_req(image_data)
            return jsonify({"error": "Request to model server failed", "details": str(e)}), 500

######################################### FLASK HANDLER METHODS ###############################################################

    def generate_3d_model_handler(self, request):
        image_data = request.json  # Assuming the request contains JSON with image details
        if not image_data:
            abort(400, description="Invalid request data")
        response, status_code = self.generate_3d_model(image_data)
        if status_code == 200:
            return response
        else:
            abort(status_code, description="Failed to generate 3D model")
    
    flask_dict = {
        "POST": {
            "/generate_3d_model": generate_3d_model_handler,
        }
    }
