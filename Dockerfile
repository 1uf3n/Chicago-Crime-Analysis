FROM python:3.11.11-slim
WORKDIR /project
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY src/ src/
COPY config/ config/
COPY sql/ sql/
COPY tests/ tests/
RUN mkdir -p data reports
CMD ["python", "src/pipeline.py"]
