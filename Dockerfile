FROM debian:stable-slim

WORKDIR /root
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl python3 python3-dev python3-venv build-essential \
  libgmp3-dev && curl -sSL https://install.python-poetry.org | python3 -
ADD poetry.lock .
ADD pyproject.toml .
ADD main.py .
ADD run.sh .
ENV PATH "/root/.local/bin:$PATH"
RUN poetry install
RUN chmod +x run.sh
ENV STREAMLIT_SERVER_PORT 8080
CMD ./run.sh
