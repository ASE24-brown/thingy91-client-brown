# Nordic Thingy:91 Frontend

Welcome! This is the Frontend repo for the Nordic Thingy:91, an easy-to-use battery-operated prototyping platform for cellular IoT. This repository is part of the project of the Brown team for the Advanced Software Engineering class in 2024.

## Table of Contents

- [Nordic Thingy:91 Frontend](#nordic-thingy91-frontend)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Starting with Docker](#using-docker)
- [Starting without Docker](#without-docker)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/ASE24-brown/thingy91-client-brown.git
   ```

2. Go inside the folder:
   
   ```sh
   cd thingy91-client-brown
   ```

## Using Docker

1. Download Docker and install it if not installed

   ```sh
   https://www.docker.com/products/docker-desktop/
   ```

2. Create a shared Docker network (needed for frontend and backend communication)
   ```sh
   docker network create shared_network
   ```

3. Launching Docker
   ```sh
   docker-compose up --build
   ```

## Without Docker

1. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
2. Activate the newly created environment:
   
   On Mac OS
   ```sh
   source venv/bin/activate
   ```

   On Windows use
   ```sh
   venv\Scripts\activate
   ```

4. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

5. Run in a terminal:

   ```sh
   python app.py
   ```

## Environment Variables

This project requires certain environment variables to be set. Create a ⁠ .env ⁠ file in the root directory of the project with the following content:

```properties
CLIENT_ID=client-id
CLIENT_SECRET=client-secret
AUTH_SERVER_URL=http://localhost:8001
```
