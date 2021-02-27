FROM python:3.8-alpine

WORKDIR /code

# Install requirements
RUN apk add proj-util g++ geos proj proj-dev build-base nodejs-current npm
ENV PROJ_DIR=/usr

# Setup python
COPY requirements.txt .
RUN  pip install -U setuptools pip
RUN pip install -r requirements.txt

# Setup and build frontend
COPY frontend/package* ./frontend/
WORKDIR /code/frontend
RUN npm ci

COPY frontend/ .
RUN npm run build

WORKDIR /code
COPY . .
EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
