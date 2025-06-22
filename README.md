# REMIXER-AI

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

## Health Checks & Monitoring

- **Backend health endpoint:**
  - `/healthz` (Flask app, returns 200 OK if backend is healthy)
- **Frontend health endpoint:**
  - `/healthz` (React app, returns 200 OK if frontend is healthy)

You can use a free uptime monitoring service (such as [UptimeRobot](https://uptimerobot.com/) or [BetterStack](https://betterstack.com/)) to monitor these endpoints and get alerts if your app goes down.

**How to set up monitoring:**
1. Deploy your app to staging or production.
2. Copy the public URLs for your backend and frontend.
3. Add the `/healthz` path to each URL (e.g., `https://your-frontend-url/healthz`).
4. Add these URLs to your monitoring service.

This will help you catch outages and issues early!

---

## Security Best Practices

- **Enable 2FA** on your GitHub account and for all collaborators.
- **Use GitHub Secrets** for sensitive values in workflows (e.g., GCP keys, tokens).
- **Use Google Secret Manager** for secrets in your cloud environment.
- **Never commit secrets** (API keys, passwords, etc.) to your repository.
- **Enable Dependabot** in your repo for automated security updates to dependencies.
- **Review permissions** for your Google Cloud and GitHub accounts regularly.

**How to enable Dependabot:**
1. Go to your GitHub repo → Settings → Security → Code security and analysis.
2. Enable Dependabot alerts and security updates.

Following these steps will help keep your app and data safe.

---

## Documentation

- The `README.md` provides setup, deployment, and security instructions.
- For API documentation, document your backend endpoints (e.g., `/healthz`, `/api/...`) in a dedicated section or file.
- Add usage examples for key features and endpoints.
- Keep documentation up to date as your app evolves.

---

## Testing

- Automated tests are located in the `flask_app/tests/` and `tests/` directories.
- To run backend tests locally:
  ```sh
  cd flask_app
  DJ.venv\Scripts\pytest.exe tests
  ```
  Or, if using a global Python environment:
  ```sh
  pytest tests
  ```
- Add more tests for new features and critical paths.
- Consider adding frontend tests (e.g., using Jest or React Testing Library).
- Ensure your CI workflow runs tests on every push or pull request.

---

*This section is up to date with the current Docker and Docker Compose setup for this project.*
