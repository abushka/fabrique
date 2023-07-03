# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-alpine as base


FROM base AS deps
# Install dependencies in separate stage because some additional packages are needed
# to build some of the dependencies. These packages are not needed in the final image.
# So, we install them in a separate stage, and then copy the dependencies over to the
# final image.

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# Save the virtual environment to /venv to prevent permissions issues.
RUN --mount=type=cache,target=/root/.cache/pip --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m venv /venv && \
    . /venv/bin/activate && \
    python -m pip install -r requirements.txt


FROM base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ARG USER=django
ARG WORKDIR=/app
WORKDIR ${WORKDIR}

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
# Add curl to base image to support health checks.
ARG UID=10001
ARG GID=10001
RUN addgroup \
    --gid ${GID} \
    ${USER} && \
    adduser \
    --disabled-password \
    --gecos "" \
    --home ${WORKDIR} \
    --shell /sbin/nologin \
    --uid ${UID} \
    --ingroup ${USER} \
    ${USER}

# Define static and media volumes so that they can be shared between containers and accessed by container user.
VOLUME /app/static
VOLUME /app/media
RUN mkdir -p /app/static && \
    mkdir -p /app/media && \
    chown -R ${UID}:${GID} /app/static && \
    chown -R ${UID}:${GID} /app/media

# Copy the virtual environment from the deps stage.
COPY --from=deps --chown=${UID}:${GID} /venv /venv

# Add the virtual environment to the path.
ENV PATH="/venv/bin:$PATH"

# Copy the source code into the container.
COPY --chown=${UID}:${GID} . /app

# Ensure that entrypoint.sh is executable.
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to the script that will run the application.
ENTRYPOINT ["/app/entrypoint.sh"]

# Set the command to run the application.
CMD ["gunicorn"]

# Switch to the non-privileged user to run the application.
USER ${USER}

# Expose the port that the application listens on.
EXPOSE 8000
