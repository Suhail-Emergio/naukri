FROM python:${PYTHON_VERSION}-slim as base

# Prevent Python from writing pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Kolkata

WORKDIR /naukri

# Install system dependencies + procps for ps, cron, tzdata
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    cron \
    procps \
    tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    echo "Asia/Kolkata" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies with caching and bind mount
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir -r requirements.txt && \
    pip install six

# Copy source code into container
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port your app listens on
EXPOSE 8007

# Run entrypoint to start cron and the app
CMD ["/entrypoint.sh"]