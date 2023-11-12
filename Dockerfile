FROM python:3.10.2-alpine
ENV EMAIL_USERNAME=your_email_username
ENV EMAIL_PASSWORD=your_email_password
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && python -m pip install --upgrade pip
COPY . .
CMD ["python", "main.py", "runserver", "0.0.0.0:5000"]