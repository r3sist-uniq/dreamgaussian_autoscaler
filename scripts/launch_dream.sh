#!/bin/bash
echo "launch_dream.sh" | tee -a /root/debug.log

SERVER_DIR="/home/workspace/vast-pyworker"

start_server() {
    if [ ! -d "$1" ]
    then
        wget -O - https://raw.githubusercontent.com/r3sist-uniq/dreamgaussian_autoscaler/main/start_server.sh | bash -s "$2"
    else
        $1/start_server.sh "$2"
    fi
}

start_server "$SERVER_DIR" "dreamgaussian"
echo "start_server done successfully"

# Function to clone repo, install dependencies, and start FastAPI server
start_3d_inference_service() {
  # Define the service directory and repository URL
  APP_DIR="/home/workspace/launch_autoscaler"
  REPO_URL="https://github.com/SehajDxstiny/launch_autoscaler.git"

  # Clone the repository if it doesn't exist
  if [ ! -d "$APP_DIR" ]; then
    echo "Cloning 3D inference repository..." | tee -a /root/setup.log
    git clone $REPO_URL $APP_DIR
  else
    echo "Repository already exists. Pulling latest changes..." | tee -a /root/setup.log
    cd $APP_DIR
    git pull
  fi

  # Navigate to service directory and install dependencies
  cd $APP_DIR
  echo "Installing dependencies..." | tee -a /root/setup.log
  chmod +x dependencies.sh
  ./dependencies.sh

  # Start the FastAPI service
  echo "Starting FastAPI service..." | tee -a /root/setup.log
  uvicorn 3d_inference:app --host 0.0.0.0 --port 5000 &>> /root/service.log &

  # Check if the service is running
  echo "Verifying service startup..." | tee -a /root/setup.log
  APP_PID=$(ps aux | grep uvicorn | grep -v grep | awk '{print $2}')
  if [ -z "$APP_PID" ]; then
    echo "Service failed to start. See /root/service.log for details." | tee -a /root/setup.log
  else
    echo "Service is up and running." | tee -a /root/setup.log
  fi
}

# Call the function to start the 3D inference service
start_3d_inference_service