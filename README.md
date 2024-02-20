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

#### Install Dependencies

Install all required packages listed in requirements.txt.

```bash
pip install -r requirements.txt
```

#### Virtual Environment

It's recommended to use a virtual environment for Python projects to manage dependencies separately for each project.

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Environment Variables

Create a .env file in the root directory of the project and fill it with your MongoDB URI

#### Running the Application

```bash
uvicorn main:app --reload
```

This will start the FastAPI application on http://127.0.0.1:8000. You can access the API documentation at http://127.0.0.1:8000/docs.
