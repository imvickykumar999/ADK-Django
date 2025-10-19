# Use the official Python image as a base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Expose the port (Gunicorn will run on this port)
EXPOSE 8000

# Run collectstatic to prepare static files
RUN python manage.py collectstatic --noinput

# Use Gunicorn as the production application server
# Replace 'myadk.wsgi' with the path to your project's WSGI file if your project name is different.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myadk.wsgi:application"]
