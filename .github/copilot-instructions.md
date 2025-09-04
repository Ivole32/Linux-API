# Linux-API Server

Linux-API is a FastAPI-based Python web server that provides system monitoring and information endpoints for Linux machines. It exposes REST APIs for system information, process monitoring, user management, and system metrics.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Quick Start and Working Effectively

### Bootstrap and Run the Server
1. **Install dependencies**: `pip install -r requirements.txt` -- takes ~8 seconds
2. **Start the server**: `python -m uvicorn server:app --host 0.0.0.0 --port 8000`
3. **Start with auto-reload for development**: `python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000`
4. **Access documentation**: Navigate to `http://localhost:8000/docs` for interactive API documentation

### Critical Authentication Information
- **Admin API Key**: The server automatically creates an admin user on first startup and prints the admin key to console as: `Init admin key: [LONG_HEX_STRING]`
- **Save the admin key immediately** - you need it to create additional users and access admin endpoints
- **All endpoints except "/" and "/docs" require authentication** via `x-api-key` header

## API Testing and Validation

### Test Basic Functionality
```bash
# Test server is running
curl http://localhost:8000/

# Test with admin key (replace YOUR_ADMIN_KEY with actual key from startup)
curl -H "x-api-key: YOUR_ADMIN_KEY" http://localhost:8000/system/system-infos

# Create a regular user
curl -X POST -H "x-api-key: YOUR_ADMIN_KEY" "http://localhost:8000/admin/user/create?username=testuser&role=user"

# Test with user key
curl -H "x-api-key: USER_API_KEY" http://localhost:8000/system/uptime
```

### Complete Validation Scenario
Always perform this end-to-end validation after making changes:
1. Start the server and capture the admin key from console output
2. Test root endpoint: `curl http://localhost:8000/`
3. Test system info with admin key: `curl -H "x-api-key: ADMIN_KEY" http://localhost:8000/system/system-infos`
4. Create a test user: `curl -X POST -H "x-api-key: ADMIN_KEY" "http://localhost:8000/admin/user/create?username=testuser&role=user"`
5. Test user access to system endpoints: `curl -H "x-api-key: USER_KEY" http://localhost:8000/system/uptime`
6. Verify user cannot access admin endpoints: `curl -H "x-api-key: USER_KEY" http://localhost:8000/admin/admin-area` (should return 403)

## Key Architecture Components

### Main Files
- `server.py` - FastAPI application entry point with middleware and router configuration
- `requirements.txt` - Python dependencies (FastAPI, Uvicorn, slowapi, pydantic, bcrypt, psutil)
- `users.db` - SQLite database created automatically on first run

### Core Directories
- `api/endpoints/` - API route definitions organized by access level:
  - `unauthenticated_endpoints.py` - Public endpoints (/, /docs)
  - `user_endpoints.py` - User-level authenticated endpoints
  - `admin_endpoints.py` - Admin-only endpoints
  - `system_endpoints.py` - System monitoring endpoints
  - `mixed_endpoints.py` - Mixed access level endpoints
- `core_functions/` - Business logic and utilities:
  - `auth.py` - API key authentication and authorization
  - `user_database.py` - SQLite user management with secure password hashing
  - `infos.py` - System information gathering (CPU, memory, disk, processes)
  - `load_monitor.py` - Background thread for CPU and system load monitoring
  - `limiter.py` - Rate limiting configuration
  - `threads.py` - Thread management utilities

### Available API Endpoints
```
GET  /                          # Landing page (unauthenticated)
GET  /docs                      # API documentation (unauthenticated)
GET  /system/system-infos       # System information (user+)
GET  /system/uptime            # System uptime (user+)
GET  /system/processes         # Running processes list (user+)
GET  /system/system-user       # System user information (user+)
GET  /system/avg-load          # System load averages (user+)
GET  /admin/admin-area         # Admin test endpoint (admin only)
GET  /admin/users              # List all users (admin only)
POST /admin/user/create        # Create new user (admin only)
GET  /user/user-info           # Current user info (user+)
DELETE /user/delete            # Delete current user (user+)
```

## Development Guidelines

### Making Changes
- **Always test authentication** - Ensure your changes don't break the API key system
- **Test rate limiting** - All endpoints have rate limits; respect them during testing
- **Monitor background threads** - The LoadMonitor runs continuously; ensure changes don't affect it
- **Database schema** - Be careful with user_database.py changes as they affect the SQLite schema

### No Testing Infrastructure
- This repository has no automated tests, linting, or CI/CD pipelines
- Always perform manual validation using the complete validation scenario above
- Use the interactive API docs at `/docs` for testing endpoint changes

### Security Considerations
- API keys are 64-character hex strings with salted hashing
- User database uses SQLite with secure password practices
- All endpoints except root and docs require authentication
- Rate limiting is applied to all endpoints via slowapi

## Common Issues and Solutions

### Database Issues
- **Database locked**: Stop all server instances before debugging database issues
- **Missing admin key**: If you lose the admin key, delete `users.db` and restart the server
- **Permission errors**: Ensure the server has write permissions in the working directory

### Performance Notes
- **LoadMonitor impact**: Background monitoring uses minimal resources but runs continuously
- **Rate limits**: Default limits are conservative (5-10 requests/minute per endpoint)
- **Process listing**: `/system/processes` can return large responses on busy systems

## Startup Time Expectations
- **Dependency installation**: ~8 seconds with `pip install -r requirements.txt`
- **Server startup**: ~2-3 seconds including database initialization
- **First admin user creation**: Automatic on first startup, prints key to console

## Example Common Tasks

### Adding a New Endpoint
1. Choose appropriate endpoint file based on access level needed
2. Import required dependencies and authentication decorators
3. Add rate limiting with `@limiter.limit("N/minute")`
4. Test with appropriate API key level
5. Validate using the complete validation scenario

### Adding System Information
1. Add collection logic to `core_functions/infos.py`
2. Create endpoint in `api/endpoints/system_endpoints.py`
3. Test with both admin and user API keys
4. Verify response format matches existing patterns

### Repository Status
- **No tests**: Manual validation required for all changes
- **No linting**: No automated code style enforcement
- **No CI/CD**: No automated builds or deployments
- **Database**: Uses SQLite, file created automatically
- **Dependencies**: All managed through requirements.txt, no additional system packages needed