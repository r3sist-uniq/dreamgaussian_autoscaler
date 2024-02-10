#!/bin/bash
echo "launch_image_to_3d.sh" | tee -a /root/debug.log

# Define server directory where your service code resides
SERVER_DIR="/home/workspace/your_service_directory"

# Function to start your service, handling both initial setup and server start
start_service() {
    if [ ! -d "$1" ]; then
        echo "Setting up the service environment..."
        # Setup commands similar to your provided bash script
        apt-get update -y && \
        apt-get install -y libegl-dev libgl1-mesa-glx libglm-dev

        pip install vastai flask fastapi pyyaml \
        && git clone https://github.com/dreamgaussian/dreamgaussian \
        && cd dreamgaussian \
        && pip install -r ./requirements.txt \
        && git clone --recursive https://github.com/ashawkey/diff-gaussian-rasterization \
        && pip install ./diff-gaussian-rasterization \
        && pip install ./simple-knn \
        && pip install git+https://github.com/NVlabs/nvdiffrast/ \
        && pip install git+https://github.com/ashawkey/kiuikit \
        && rm -rf /root/.cache/pip

        echo "Service environment setup completed." | tee -a /root/debug.log
    else
        echo "Service directory already exists. Assuming environment is set." | tee -a /root/debug.log
    fi

    # Start the FastAPI service
    echo "Starting the FastAPI service for image to 3D model conversion..." | tee -a /root/debug.log
    uvicorn main:app --host 0.0.0.0 --port 5000 &>> $SERVER_DIR/service.log &
    echo "FastAPI service launched." | tee -a /root/debug.log
}

# Call the start_service function with the server directory
start_service "$SERVER_DIR"

# Check if the service is running. Adjust the command to suit how you verify the service's operation.
SERVICE_PID=$(ps aux | grep uvicorn | grep -v grep | awk '{print $2}')

if [ -z "$SERVICE_PID" ]; then
    echo "Service failed to start. Check /root/debug.log and $SERVER_DIR/service.log for details." | tee -a /root/debug.log
else
    echo "Service is running." | tee -a /root/debug.log
fi
