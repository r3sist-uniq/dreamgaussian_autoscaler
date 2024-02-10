from flask import abort

from backend import GenericBackend
from sdauto.metrics import Metrics

INSTANCE_ID = "localhost"
INSTANCE_PORT = '5000'
MODEL_SERVER = INSTANCE_ID + ":" + INSTANCE_PORT

class Backend(GenericBackend):
  def __init__(self, container_id, control_server_url, master_token, send_data):
    metrics = Metrics(id=container_id, master_token=master_token, control_server_url=control_server_url, send_server_data=send_data)
    super().__init__(master_token=master_token, metrics=metrics)
    self.model_server_addr = MODEL_SERVER

  def imageTo3d(self, model_request):
    return super().generate(model_request, self.model_server_addr, "inference_with_image", lambda r: r.content, metrics=True)

def imageto3d_handler(backend, request):
  auth_dict, model_dict = backend.format_request(request.json)
  if auth_dict:
    if not backend.check_signature(**auth_dict):
      abort(401)
  code, content, _ = backend.imageTo3d(model_dict)
  if code == 200:
    return content
  else:
    print(f"3d generation failed failed with code {code}")
    abort(code)

flask_dict = {
    "POST" : {
      "generate_3d_model" : imageto3d_handler
    }
}