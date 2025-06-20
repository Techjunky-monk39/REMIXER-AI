## Running the Project with Docker

This project is containerized using Docker and Docker Compose for a reproducible Python environment.

### Project-Specific Docker Details
- **Python Version:** 3.8-slim (as specified in the Dockerfile)
- **Virtual Environment:** The application runs inside a Python virtual environment (`.venv`) created during the build process.
- **Dependencies:** All Python dependencies are installed from `requirements.txt` during the build.
- **User:** The container runs as a non-root user (`appuser`) for improved security.

### Environment Variables
- No required environment variables are set by default in the Dockerfile or Compose file.
- If your application requires environment variables, you can add them to a `.env` file and uncomment the `env_file` line in `docker-compose.yml`.

### Ports
- **No ports are exposed by default.**
- If your application (e.g., a Flask app) listens on a port (such as 8080), the compose files already expose the correct ports.

### Build and Run Instructions
1. **Build and start the application (production):**
   ```sh
   docker compose -f docker-compose.prod.yaml up --build
   ```
2. **(Optional) Add environment variables:**
   - Create a `.env` file in the project root if needed.
   - Uncomment the `env_file` line in `docker-compose.prod.yaml`.
3. **(Optional) Expose application ports:**
   - The compose files already expose the necessary ports for your app.

### Special Configuration
- No external services (databases, caches, etc.) are configured by default.
- If you add external services, update `docker-compose.prod.yaml` accordingly (e.g., add `depends_on`, `networks`, or `volumes`).

---

*This section is up to date with the current Docker and Docker Compose setup for this project.*