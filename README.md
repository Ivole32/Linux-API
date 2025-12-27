# Linux-API

[![PyPI version](https://badge.fury.io/py/linux-api.svg)](https://pypi.org/project/linux-api/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/Ivole32/Linux-API)](LICENSE)

A modern, secure REST API server for Linux system monitoring and management. Built with FastAPI and designed for production use.

## 🚀 Features

- **System Monitoring:** Real-time CPU, memory, disk, and network statistics
- **Process Management:** View running processes and system load
- **User Management:** Role-based access control (admin/user)
- **Secure Authentication:** API key-based authentication with bcrypt hashing
- **Rate Limiting:** Built-in rate limiting to prevent abuse
- **Interactive Documentation:** Auto-generated OpenAPI/Swagger docs
- **Easy Deployment:** Run manually, via pip, or as a systemd service

[📋 See full feature list](https://github.com/Ivole32/Linux-API/wiki/Features)

## 📦 Installation

### Quick Install with pip

```bash
pip install linux-api
linux-api
```

### From Source

```bash
git clone https://github.com/Ivole32/Linux-API.git
cd Linux-API
pip install .
```

## 📚 Documentation

Comprehensive guides for different deployment scenarios:

- 📖 [Manual Hosting Guide](https://github.com/Ivole32/Linux-API/wiki/Manual-Hosting) - Run directly from source
- 📖 [pip Installation Guide](https://github.com/Ivole32/Linux-API/wiki/pip-Hosting) - Install as a Python package
- 📖 [systemd Service Guide](https://github.com/Ivole32/Linux-API/wiki/Systemd-Hosting) - Run as a background service

## 🌐 Demo & API Docs

- **Live Demo:** Currently down
- **Interactive API Documentation:** Available at `/docs` endpoint when running

## 🛠️ Requirements

- **OS:** Linux only
- **Python:** 3.11 or newer
- **Privileges:** `sudo` required for ports below 1024

## 🔒 Security Notes

- Admin API key is generated on first startup - save it securely
- All endpoints (except `/` and `/docs`) require authentication
- Rate limiting is enforced per endpoint
- Use a dedicated user account for production deployments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the terms specified in the repository.

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/Ivole32/Linux-API/issues)
- **PyPI:** [https://pypi.org/project/linux-api/](https://pypi.org/project/linux-api/)
- **Support the project:** [☕ Buy me a coffee on Ko-fi](https://ko-fi.com/ivole32)

---

Made with ❤️ by [Ivole32](https://github.com/Ivole32)
