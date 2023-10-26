import os
import time
import docker
import zipfile
from decouple import config
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the folder to monitor
folder_to_watch = "C:\\Users\\Oscar\\Desktop\\listener\\zipFile"
folder_to_convertDocker = "C:\\Users\\Oscar\\Desktop\\listener\\jobsUnzipped"

# Docker Hub username, image name, and tag
dockerhub_username = config('docker_username')
image_name = "dw_main"
tag = "latest"  # Replace with the desired tag
password = config('docker_pw')

# Define jobs 

class NewFolderHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer
        self.stop_running = False

    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.lower().endswith('.zip'):
            self.stop_running = True
            self.observer.stop()
            new_folder = event.src_path
            print(f"New folder created: {new_folder}")
            time.sleep(3) # Allow folder to be created completely first

            zip_file_path = new_folder
            extraction_path = folder_to_convertDocker

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_path)
            print(f'Zip file unzipped successfully in {extraction_path}')

            # Go into the new folder
            new_folder = extraction_path
            os.chdir(new_folder)

            # Use os.listdir() to get a list of all items in the directory.
            items = os.listdir(new_folder)

            # Filter the items to include only directories (folders).
            folders = [item for item in items if os.path.isdir(os.path.join(new_folder, item))]

            # Get into job folder to get the sh file to run the pipeline
            jobDetailsFolders = [folder for folder in folders if folder != 'lib']
            jobDetailsFolders = jobDetailsFolders[0]

            # Get into script folder
            scriptFolderPath = os.path.join(new_folder, jobDetailsFolders)
            detailFiles = os.chdir(scriptFolderPath)
            scriptFiles = os.listdir(detailFiles)

            # Run sh script file for the specific jobs
            shScriptFiles = jobDetailsFolders + "_run.sh"
            shFilePath = os.path.join(scriptFolderPath, shScriptFiles)
            
            # Define folder to store docker files
            jobDockerFiles = "C:\\Users\\Oscar\\Desktop\\listener\\job_dockers"
            shScriptFilesPath = f"/talend/{jobDetailsFolders}/{jobDetailsFolders}_run.sh"

            # Create a Dockerfile
            DockerFilePath = folder_to_convertDocker + "\\Dockerfile"
            with open(DockerFilePath, 'w') as dockerfile:
                dockerfile.write(f"""
                                 FROM openjdk:22-jdk-slim
                                 WORKDIR /talend
                                 COPY . /talend
                                 CMD ["/bin/bash", "{shScriptFilesPath}"]
                                """)

            print(f"Dockerfile created in {jobDockerFiles}")

            time.sleep(5)

            # Push DockerFile
            # Initialize the Docker client
            client = docker.from_env()

            # Build the Docker image
            image, build_logs = client.images.build(
                path=folder_to_convertDocker,
                tag=f"{dockerhub_username}/{image_name}:{tag}",
                rm=True,  # Remove intermediate containers
            )

            # Push the Docker image to Docker Hub
            for log in build_logs:
                if "stream" in log:
                    print(log["stream"], end="")

            # Log in to Docker Hub
            client.login(username=dockerhub_username, password=password)

            # Push the image to Docker Hub
            client.images.push(f"{dockerhub_username}/{image_name}", tag=tag)

            print("Image pushed to Docker Hub")
            
# Init and setting up observer
if __name__ == "__main__":
    observer = Observer()
    event_handler = NewFolderHandler(observer)
    observer.schedule(event_handler, path=folder_to_watch, recursive=False)
    observer.start()

    try:
        while not event_handler.stop_running:
            time.sleep(2)
            print("Running...")
    except KeyboardInterrupt:
        observer.stop()

    observer.join()