# API ClusterOne-Web 🧬

Fast API to serve the algorithm of clustering "ClusterOne"

## Installation 🖥️

    - Install Docker
    - Install Docker Compose
    - Clone the repository
    - Run the command: docker-compose build
    - Run the command: docker-compose run --rm web_server alembic upgrade head
    - Run the command: docker-compose up

## Pre-Loaded Data (Optional) 🐳

    - The data is loaded from the file: `example/collins2007.txt`
    - Run the command: docker-compose up -d web_server
    - Run the command: docker ps 
    - Copy the container id of the web_server
    - Run the command: docker exec -it <container_id> bash
    - Run the command: python3 scripts/protein.py
    - Run the command: python3 scripts/ppi_graph.py

## Usage

        - Open the browser and go to the address: http://localhost:8000/docs
        - Click on the button "Try it out"
        - Click on the button "Execute"
        - The result will be displayed in the "Response body" section
