FROM python:3.14-slim

WORKDIR /root
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvbin/uv
ENV PATH "/uvbin:$PATH"

COPY pyproject.toml uv.lock .
RUN uv sync --frozen --no-dev

COPY main.py valuation.py .
ENV STREAMLIT_SERVER_PORT 8080
# Health check moved to /_stcore/health in current Streamlit; configure that path
# on the deployment platform's health check instead of patching site-packages.
CMD uv run streamlit run main.py
