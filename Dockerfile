FROM debian:stable-slim

WORKDIR /root
RUN apt-get update && apt-get upgrade -y && apt-get install -y curl python3 python3-dev python3-venv build-essential \
  libgmp3-dev && curl -sSL https://install.python-poetry.org | python3 -
ADD poetry.lock .
ADD pyproject.toml .
ADD main.py .
ENV PATH "/root/.local/bin:$PATH"
RUN poetry install -vvv
ENV STREAMLIT_SERVER_PORT 8080
RUN poetry run echo $PATH
RUN poetry run which python
RUN poetry run which streamlit
CMD ["poetry", "run", "streamlit", "run", "main.py"]
