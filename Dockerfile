# Use the official Python image as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire current directory into the container at /app
COPY ./app /code/app


# Create the my_cache folder if it doesn't exist (ensures write permissions)
RUN mkdir -p app/my_cache

# Set the environment variable for caching using the recommended HF_HOME name
ENV HF_HOME=./app/my_cache

# Grant broader permissions to the cache directory (use with caution)
RUN chmod -R 775 app/my_cache

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

