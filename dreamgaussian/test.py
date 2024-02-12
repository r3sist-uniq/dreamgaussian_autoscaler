from flask import abort, jsonify
from backend import GenericBackend
from dreamgaussian.metrics import Metrics  # Adjust the import path as needed

INSTANCE_ID = "localhost"
INSTANCE_PORT = '5000'
MODEL_SERVER = INSTANCE_ID + ":" + INSTANCE_PORT

class Backend(GenericBackend):
    def __init__(self, container_id, control_server_url, master_token, send_data):
        metrics = Metrics(id=container_id, master_token=master_token, control_server_url=control_server_url, send_server_data=send_data)
        super().__init__(master_token=master_token, metrics=metrics)
        self.model_server_addr = MODEL_SERVER

    def generate_3d_model(self, image_data):
        def response_func(response):
            try:
                glb_url = response.json().get('glb_url')
                return {"glb_url": glb_url}
            except ValueError:
                print(f"[Backend] JSONDecodeError for response: {response.text}")
                return None

        status_code, result, _ = super().generate(image_data, self.model_server_addr, "generate_3d", response_func, metrics=True)
        if status_code == 200:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Failed to generate 3D model"}), status_code

######################################### FLASK HANDLER METHODS ###############################################################

    def generate_3d_model_handler(backend, request):
        auth_dict, model_dict = backend.format_request(request.json)
        if auth_dict:
            if not backend.check_signature(**auth_dict):
                abort(401)

        code, content, _ = backend.generate_3d_model(model_dict)
        if code == 200:
            return content
        else:
            print(f"3d generation failed with code {code}")
            abort(code)
    
    flask_dict = {
        "POST": {
            "/generate_3d_model": generate_3d_model_handler,
        }
    }
