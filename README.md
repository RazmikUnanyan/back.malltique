# Back Malltique

Back Malltique is the backend for the Malltique project. This project provides an API for managing user data, product information, and other application elements. It is built with Python using Django and supports containerization through Docker.

## Project Structure

- **app/**  
  Contains the core applications, including:  
  - `core/` — main logic and utilities of the project.  
  - `product/` — product-related data management.  
  - `user/` — user-related data management.

- **proxy/**  
  Configuration for request proxying, if needed.

- **scripts/**  
  Scripts for automating various tasks related to development and deployment.

- **.env and .env.sample**  
  Environment variable files. `.env` is used locally, and `.env.sample` provides a template for development.

- **docker-compose.yml and docker-compose-deploy.yml**  
  Files for managing Docker containers during development and deployment.

- **requirements.txt and requirements.dev.txt**  
  Dependency files:  
  - `requirements.txt` — for production dependencies.  
  - `requirements.dev.txt` — for development dependencies.

## Key Technologies

- **Django** — web framework for building the backend.  
- **Docker** — containerization for simplified deployment and dependency management.  
- **Flake8** — tool for code quality checks.

