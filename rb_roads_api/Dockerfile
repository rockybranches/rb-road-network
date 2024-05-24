# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# run install commands
RUN apt update \
    && apt install \
        -yyq --no-install-recommends \
         acl sudo python3-pip \
    && pip3 install poetry

# setup non-root user
RUN mkdir -p /var/run
VOLUME /var/run/docker.sock
RUN groupadd -r -g 1000 appuser && \
    groupadd -f docker \
    && useradd -m -r -u 1000 -g appuser appuser \
    && usermod -aG sudo,docker appuser \
    && mkdir -p /home/appuser/.local/share/pypoetry/venvs \
    && mkdir -p /home/appuser/.cache/pypoetry \
    && mkdir -p /home/appuser/.config/pypoetry \
    && mkdir -p /home/appuser/.cache/pip \
    && mkdir -p /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/pypoetry/venvs \
    && chown -R appuser:appuser /home/appuser/.cache/pypoetry \
    && chown -R appuser:appuser /home/appuser/.config/pypoetry \
    && chown -R appuser:appuser /home/appuser/.cache/pip \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && chown -R appuser:appuser /home/appuser/.local/share/virtualenvs \
    && echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER appuser

# setup build environment variables
ENV USER=appuser
ENV RB_SRC=/home/appuser/rb_app
ENV RB_DATA=/home/appuser/rb_data
WORKDIR $RB_SRC/rb_roads_api

# Copy the current directory contents into the container
COPY . $RB_SRC/rb_roads_api

# mount data volume
RUN mkdir -p $RB_DATA
VOLUME $RB_DATA

# Use poetry to install dependencies
RUN poetry install

# setup docker socket permissions
RUN --mount=type=cache,target=/var/run/docker.sock \
    sudo setfacl --modify user:$USER:rw /var/run/docker.sock && \
    sudo chown -R appuser:docker /var/run/docker.sock

# Make port available to the world outside this container
ENV PORT=5000
EXPOSE "${PORT}"

# Run api.py when the container launches
CMD ["sudo", "-E", "poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
