from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import ByteString
import yaml
import os, requests
from fastapi.responses import FileResponse
import base64
from fastapi.middleware.cors import CORSMiddleware


vast_tcp_port_x = os.getenv('VAST_TCP_PORT_8081')
ip_address = os.getenv('PUBLIC_IPADDR')

address = f"https://{ip_address}:{vast_tcp_port_x}/"
print(address)

class ImageData(BaseModel):
  data: str
  extension: str
  file_name: str

def update_yaml_file(file_path, new_value, key):
  with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
  data[key] = new_value
  with open(file_path, 'w') as file:
    yaml.dump(data, file)

def save_image_base64(base64_string, file_path):
    # Decode the base64 string to bytes
    image_data = base64.b64decode(base64_string)
    # Write the bytes to a file
    with open(file_path, 'wb') as file:
        file.write(image_data)

def save_image_with_url(url, file_path):
  with open(file_path, 'wb') as file:
    response = requests.get(url)
    file.write(response.content)

def send_notification(stage, status, message, contact_url):
  payload = {
    "stage": stage,
    "status": status,
    "message": message
  }
  try:
    requests.post(contact_url, json=payload)
  except requests.RequestException as e:
    print(f"Failed to send notification for {stage}: {e}")

#This is needed because setting to False gives error sometimes
update_yaml_file('./dreamgaussian/configs/image.yaml', True, "force_cuda_rast")

app = FastAPI()

origins = [
    "http://arrival.so",
    "https://arrival.so",
    "http://app.arrival.so",
    "https://app.arrival.so"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
  #TODO add security measures?
  base_directory = "."
  file_location = os.path.join(base_directory, file_path)
  print(file_location)
  if not os.path.isfile(file_location):
    raise HTTPException(status_code=404, detail="File not found")
  return FileResponse(file_location)

@app.get("/sayhello")
async def say_hello():
    print('yup worked')
    return {"answer": "hello"}


@app.post("/inference_with_image")
async def get_file_urls(image_data: ImageData): 
  # Validate the Image
  #TODO do better validation?
  if not image_data.data:
    raise HTTPException(status_code=400, detail="Image is required")

  file_path = f"./dreamgaussian/data/{image_data.file_name}.{image_data.extension}"
    
  preprocessed_file_path = f"./dreamgaussian/data/{image_data.file_name}_rgba.png" 
  file_name = image_data.file_name

  #save image locally
  save_image_base64(image_data.data,file_path)
  
  #python process.py data/name.jpg
  preprocess_command = ["python", "./dreamgaussian/process.py", f"{file_path}"] 
  
  #python main.py --config configs/image.yaml input=data/name.jpg save_path=results/name.mp4 mesh=results/name.obj
  #TODO confirm if the name should be _mesh for the first command. 
  stage1_command = ["python", "./dreamgaussian/main.py", "--config", "./dreamgaussian/configs/image.yaml", f"input={preprocessed_file_path}", f"save_path={file_name}", "mesh_format=glb"]
  stage2_command= ["python", "./dreamgaussian/main2.py", "--config", "./dreamgaussian/configs/image.yaml", f"input={preprocessed_file_path}", f"save_path={file_name}", "mesh_format=glb"]

  #python kire logs/name.obj --save_video name.mp4 --wogui
  save_video_command = ["kire", f"./logs/{file_name}.glb", "--save_video", f"./logs/{file_name}.mp4", "--wogui", "--force_cuda_rast"]

  try:
    subprocess.run(preprocess_command, check=True)
    print('preprocess done')
    
    subprocess.run(stage1_command, check=True)
    print('command1 done')

    subprocess.run(stage2_command, check=True)
    print('command2 done')

    subprocess.run(save_video_command, check=True)
    print('save video done')

  except subprocess.CalledProcessError as e:
    raise HTTPException(status_code=500, detail=f"An error occurred while executing a subprocess: {e}")

  # Return the path of the saved video
  return {'video_path': f"/logs/{file_name}.mp4", 'glb': f"/logs/{file_name}.glb","instance_public_url": address}
  