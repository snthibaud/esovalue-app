FROM debian:stable-slim

WORKDIR /root
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl python3 python3-dev python3-venv build-essential \
  libgmp3-dev && curl -sSL https://install.python-poetry.org | python3 -
COPY poetry.lock .
COPY pyproject.toml .
COPY main.py .
ENV PATH "/root/.local/bin:$PATH"
RUN poetry install
ENV STREAMLIT_SERVER_PORT 8080
CMD HOME=/root poetry run streamlit run --health-check-url=health-check main.py
