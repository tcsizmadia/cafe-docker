FROM postgres:17

# Copy initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/

# Set environment variables
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_USER=postgres

# Set healthcheck
HEALTHCHECK --interval=5s --timeout=5s --retries=5 \
  CMD ["pg_isready", "-U", "postgres"]
