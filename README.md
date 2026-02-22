# Linux-API

Linux-API is a small REST API service for collecting and exposing metrics and user data for Linux systems. It is implemented in Python (FastAPI) and ships with Docker Compose configurations to run the required database services locally.

## Documentation
Full installation and configuration instructions are available in the [project's documentation](https://github.com/Ivole32/Linux-API/wiki/)

Please consult the manual setup first for a step-by-step deployment on Ubuntu systems.

## What this project is
- REST API backend built with FastAPI for high performance and async handling  
- User & authentication system with permission checks and admin controls  
- Metrics & monitoring system for observability and production diagnostics  
- Per-route request metrics (counts, response times, percentiles, error rates)  
- Status code tracking to detect failures and anomalies  
- Global performance statistics for overall system health insights  
- TimescaleDB integration for efficient time-series storage and long-term analysis  
- Health & monitoring endpoints exposing system status and diagnostics  
- Database readiness & migration checks for operational safety  
- PostgreSQL connection pooling for performance and reliability  
- Rate limiting & security middleware to protect endpoints  
- Configurable legacy route support for backward compatibility  
- Designed for production observability, debugging, and scalability

## Support
- Issues: https://github.com/Ivole32/Linux-API/issues
- Support the project: https://ko-fi.com/ivole32

## Contributing
See the repository root for development notes and tests. If you find problems in the docs or installation steps, please open an issue.

---

Made with ❤️ by Ivole32 — https://github.com/Ivole32