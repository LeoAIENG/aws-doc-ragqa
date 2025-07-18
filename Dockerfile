# Use an official Python runtime as a parent image
# IMAGE
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# COPY
ADD . /app
COPY data/interim/category_files_df_v1.pickle /app/data/interim/category_files_df_v1.pickle
WORKDIR /app

# INSTALL
RUN uv sync --locked

# Expose the port the app runs on

ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
EXPOSE 7860

# Run the application
CMD ["uv", "run", "python", "src/application/conversation_service/app.py"]