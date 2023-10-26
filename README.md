# Automated Job Execution and Dockerization Script

This Python script, `main.py`, is designed to monitor a specific folder for the creation of new ZIP files, extract their contents, and automatically create Docker containers to execute associated job scripts.

## Prerequisites

Before using this script, make sure you have the following prerequisites:

- **Python:** Ensure you have Python installed on your system.
- **Docker:** You need Docker installed, as this script builds and pushes Docker containers to execute job scripts.
- **Docker Hub Account:** You should have a Docker Hub account to push Docker images.

## Getting Started

1. Clone or download this repository to your local machine.

2. Install Python dependencies using pip:

   ```bash
   pip install docker watchdog decouple

3. Update the config.env file with your Docker Hub username and password.

    ```env
    docker_username=your_username
    docker_pw=your_password

4. Modify the folder_to_watch and folder_to_convertDocker variables in main.py to specify the folders you want to monitor and where to unzip job scripts.

5. Make sure the Docker image name (image_name) and tag (tag) in the main.py script match your requirements.

6. Run the script

    ```bash
    python main.py

## How It Works
    The script uses the watchdog library to monitor the folder_to_watch for the creation of ZIP files.

    When a ZIP file is detected, it extracts its contents to the folder_to_convertDocker.

    The script then creates a Dockerfile for the extracted job scripts, builds a Docker image, and pushes it to Docker Hub.

    The Docker image is tagged with your specified image_name and tag.

    The script uses Docker to run the job script within a Docker container.

    The job-specific Docker image is pulled from Docker Hub and executed within the container.

## Customization
    You can modify the script to handle different ZIP file structures or job execution requirements by adjusting the folder structure and job execution logic.

    Customize the Docker image by modifying the Dockerfile template within the script.