[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/Nz6HcS3RP2iARiLEhS7sKA/d252626f-5f96-4785-ae64-1b46453187d1/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/Nz6HcS3RP2iARiLEhS7sKA/d252626f-5f96-4785-ae64-1b46453187d1/tree/main)

# FastAPI Backend Application Setup

This repository is a FastAPI application that includes user authentication, MongoDB integration, and more.

## Prerequisites

- Python 3.8 or newer
- pip
- MongoDB account (Atlas or local installation)

## Setup

### Clone the repository

```bash
git clone https://github.com/Explore-Hub-Capstone-Project/ExploreHub-Backend
cd ExploreHub-Backend
```
#### Installation steps
you can use poetry or pip 
here are the poetry instructions:
 - install poetry here: https://python-poetry.org/docs/#installing-with-pipx
 - run `poetry install`
 - `poetry run pre-commit install`
 - For formatting and linting run `poetry run pre-commit` before committing
 - Recommended: install ide extensions – Mypy, black, flake8
 - for starting server run 'poetry run start'

here are the pip instructions:

```bash
pip install -r requirements.txt
```

#### Virtual Environment

It's recommended to use a virtual environment for Python projects to manage dependencies separately for each project.

If you use poetry, it will create the virtual environment for you. 

if you don't use poetry, here are the manual steps:
#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```
## 
#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Environment Variables

Create a .env file in the root directory of the project and fill it with your MongoDB URI

#### Running the Application
if you use poetry, you would write :
```bash
poetry run start
```
if you don't use poetry, you would write:

```bash
uvicorn main:app --reload
```

This will start the FastAPI application on http://127.0.0.1:5000. You can access the API documentation at http://127.0.0.1:5000/docs.
