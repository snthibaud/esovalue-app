FROM debian:stable-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl python3 python3-dev python3-venv build-essential \
  libgmp3-dev && curl -sSL https://install.python-poetry.org | python3 -
ADD poetry.lock .
ADD pyproject.toml .
ADD main.py .
ENV PATH "/root/.local/bin:$PATH"
RUN poetry install
ENV STREAMLIT_SERVER_PORT 8080
ENV STREAMLIT_SERVER_ADDRESS "0.0.0.0"
CMD ["poetry", "run", "streamlit", "run", "main.py"]