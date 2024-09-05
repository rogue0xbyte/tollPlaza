# Use an official Python runtime as a parent image
FROM python:3.9-slim

ENV PYHTONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install ffmpeg libsm6 libxext6 --fix-missing
RUN apt-get -y install python-dev-is-python3 libatlas-base-dev --fix-missing

# Set the working directory in the container
WORKDIR /code

# Make port 8081 available to the world outside this container
EXPOSE 8081

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /code/requirements.txt
RUN pip install "uvicorn[standard]"
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the current directory contents into the container at /code
COPY ./ /code/

# Command to run the application
CMD ["uvicorn", "ui_backend:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
