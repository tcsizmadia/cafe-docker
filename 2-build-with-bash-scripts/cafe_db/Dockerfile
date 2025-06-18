FROM postgres:13

# Add initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/

# Health check
HEALTHCHECK --interval=5s --timeout=5s --retries=5 CMD pg_isready -U postgres

# Expose the default PostgreSQL port
EXPOSE 5432
