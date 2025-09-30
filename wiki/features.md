# Linux-API Features

Linux-API provides a secure, fast, and easy-to-use REST API for system monitoring and management on Linux machines.

## Key Features

- **System Information:**
  - CPU, memory, disk, and network stats
  - System uptime and load averages
  - Running processes and user sessions
- **User Management:**
  - Create, list, and delete API users (admin only)
  - Role-based access (admin/user)
- **Authentication:**
  - Secure API key authentication for all endpoints (except root/docs)
  - Admin key generated on first start
- **Rate Limiting:**
  - Per-endpoint rate limits to prevent abuse
- **API Documentation:**
  - Interactive OpenAPI docs at `/docs`
- **Background Monitoring:**
  - Continuous system load monitoring in a background thread
- **Easy Deployment:**
  - Run manually, via pip, or as a systemd service

## Example Use Cases
- Integrate with dashboards for live system stats
- Automate server health checks
- Manage users and monitor access securely
