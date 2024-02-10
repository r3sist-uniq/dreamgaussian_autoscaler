from flask import Flask, request, abort, send_from_directory
import subprocess
import base64
import yaml
import os
import requests

class ImageData:
    def __init__(self, data, extension, file_name):
        self.data = data
        self.extension = extension
        self.file_name = file_name

    @staticmethod
    def from_request(req_data):
        return ImageData(data=req_data.get('data'), extension=req_data.get('extension'), file_name=req_data.get('file_name'))

def update_yaml_file(file_path, new_value, key):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    data[key] = new_value
    with open(file_path, 'w') as file:
        yaml.dump(data, file)

def save_image_base64(base64_string, file_path):
    image_data = base64.b64decode(base64_string)
    with open(file_path, 'wb') as file:
        file.write(image_data)

class Backend():
    def __init__(self):
        self.base_directory = "./dreamgaussian/data"
        os.makedirs(self.base_directory, exist_ok=True)
        update_yaml_file('./dreamgaussian/configs/image.yaml', True, "force_cuda_rast")
    
    def inference_with_image(self):
        content = request.json
        image_data_obj = ImageData.from_request(content)
        
        if not image_data_obj.data:
            abort(400, description="Image data is required")
        
        file_path = os.path.join(self.base_directory, f"{image_data_obj.file_name}.{image_data_obj.extension}")
        save_image_base64(image_data_obj.data, file_path)

        preprocessed_file_path = f"{self.base_directory}/{image_data_obj.file_name}_rgba.png"
        file_name = image_data_obj.file_name
        
        # Define your commands here
        commands = [
            ["python", "./dreamgaussian/process.py", file_path],
            ["python", "./dreamgaussian/main.py", "--config", "./dreamgaussian/configs/image.yaml", f"input={preprocessed_file_path}", f"save_path=./dreamgaussian/results/{file_name}", "mesh_format=glb"],
            # Add more commands as needed
        ]

        for command in commands:
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                abort(500, description=f"An error occurred while executing a subprocess: {e}")
        
        # Assuming the response should include paths or URLs to the generated files
        video_path = f"./dreamgaussian/results/{file_name}.mp4"
        glb_path = f"./dreamgaussian/results/{file_name}.glb"
        
        # Return the path of the saved video and GLB model
        return {
            'video_path': video_path,
            'glb_path': glb_path,
            # Assuming 'address' needs to be constructed or passed in some way
            "instance_public_url": "https://{ip_address}:{vast_tcp_port_x}/".format(ip_address=os.getenv('PUBLIC_IPADDR'), vast_tcp_port_x=os.getenv('VAST_TCP_PORT_8081'))
        }

# Flask dict for mapping Flask routes to handler functions
flask_dict = {
    "POST": {
        "/inference_with_image": Backend().inference_with_image
    }
}
