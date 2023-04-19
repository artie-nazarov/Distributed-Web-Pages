FROM python:latest
COPY src ./src
COPY requirements.txt /
RUN pip install -r requirements.txt
CMD ["python", "src/app.py"]
