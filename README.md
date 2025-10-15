# 🛡️ Insider Threat Detection System

**Version 2.0** - Production-Ready ML System for Real-Time Insider Threat Detection

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4+-teal.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An intelligent ML-powered system that detects insider threats in real-time using hybrid ensemble learning with dual dashboard interfaces.

---

## 🎯 Overview

A production-ready machine learning system for detecting insider threats using a hybrid ensemble approach combining **XGBoost** (60%) and **LSTM** (40%) models. The system provides real-time threat detection through a FastAPI REST API with comprehensive monitoring, logging, and persistence capabilities, complemented by both a Streamlit and a modern React dashboard for visualization and interaction.

### ✨ Key Features

- **🧠 Hybrid ML Ensemble** - Balanced detection using XGBoost + LSTM
- **⚡ Real-time API** - FastAPI with async support and auto-documentation
- **🏭 Production-Ready** - Logging, metrics, database persistence, caching
- **⚙️ Configurable** - YAML + environment variables
- **📊 Observable** - Prometheus metrics, structured logging, health checks
- **🔄 Versioned** - Model version management and rollback
- **🧪 Tested** - Unit tests with pytest
- **📚 Well-Documented** - Comprehensive guides and API documentation
- **🎨 Dual Dashboards** - Streamlit for quick insights, React for modern UI/UX
- **🚀 One-Click Deploy** - PowerShell orchestration script

---

## 🚀 Quick Start (3 Minutes)

### 1. Clone & Install

```bash
git clone https://github.com/Av7danger/insider-detect.git
cd insider-detect
pip install -e .
# For React dashboard dependencies
cd web-dashboard
npm install
cd ..
```

### 2. Run Everything

Use the PowerShell script to start all services (API, Streamlit, React dashboard) and optionally run the demo and open browsers.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_everything.ps1 -RunDemo -OpenBrowser
```

This command will:
- Stop any previously running API, Streamlit, or React dev servers
- Start the FastAPI backend on `http://127.0.0.1:8000`
- Start the Streamlit dashboard on `http://localhost:8501`
- Start the React (Vite) dashboard on `http://localhost:5173`
- Wait for all services to become healthy
- Run the demo script with sample threat scenarios
- Open browser tabs for all dashboards and API docs

### 3. Access Your System

- **🎨 React Dashboard**: `http://localhost:5173` (Modern UI/UX)
- **📊 Streamlit Dashboard**: `http://localhost:8501` (Quick Analytics)
- **📖 FastAPI Swagger UI**: `http://127.0.0.1:8000/docs`
- **🔧 FastAPI OpenAPI Spec**: `http://127.0.0.1:8000/openapi.json`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Insider Threat Detection System          │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   React App     │  │  Streamlit App  │                  │
│  │  (Vite + TS)    │  │  (Analytics)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│  API Layer                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              FastAPI REST API                           │ │
│  │  • Health Checks  • Session Inference  • Statistics    │ │
│  │  • Model Info     • Batch Processing   • Metrics       │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ML Layer                                                   │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │    XGBoost      │  │      LSTM       │                  │
│  │   (60% weight)  │  │   (40% weight)  │                  │
│  └─────────────────┘  └─────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   SQLite DB     │  │   File Cache    │                  │
│  │  (Predictions)  │  │   (5min TTL)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
insider-detect/
├── app/                    # Main application
│   ├── core/              # Configuration, logging, database
│   ├── models/            # ML inference and version management
│   ├── utils/             # Feature engineering helpers
│   └── api.py             # FastAPI REST API
│
├── training/              # Model training (separate from app)
│   ├── trainers/          # XGBoost, LSTM, Attention trainers
│   ├── data/              # Data pipeline and augmentation
│   └── layers/            # Custom neural network layers
│
├── dashboard/             # Streamlit dashboard
│   └── streamlit_app.py
│
├── web-dashboard/         # React + Vite + TypeScript dashboard
│   ├── src/
│   │   ├── api.ts         # API client
│   │   ├── index.css      # Tailwind CSS entry
│   │   └── main.tsx       # Main React app
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/               # Orchestration scripts
│   └── run_everything.ps1 # PowerShell script to run all services
│
├── tests/                 # Unit tests with pytest
├── config/                # YAML configuration files
├── data/                  # Data storage
├── models/                # Trained model artifacts
├── logs/                  # Application logs
└── docs/                  # Documentation
```

---

## 🔧 Configuration

Three flexible ways to configure the system:

### 1. YAML Configuration (Recommended)

Edit `config/config.yaml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8000

model:
  xgb_weight: 0.6
  lstm_weight: 0.4
  threshold: 0.5

cache:
  enabled: true
  ttl: 300  # 5 minutes
```

### 2. Environment Variables

Create `.env` file:

```bash
API_PORT=8001
LOG_LEVEL=DEBUG
MODEL_THRESHOLD=0.5
CACHE_ENABLED=true
```

### 3. Command Line

```bash
export API_PORT=8001
python -m app.api
```

**Priority:** CLI args > Environment variables > YAML config > Defaults

---

## 🔌 API Endpoints

### Health & Info

```bash
GET  /              # Service information
GET  /health        # Health check with detailed status
GET  /model_info    # Model version and configuration
GET  /statistics    # Prediction statistics
GET  /metrics       # Prometheus metrics
```

### Inference

```bash
POST /infer_session    # Predict single session
POST /infer_batch      # Batch predictions
```

### Example Usage

```bash
curl -X POST http://localhost:8000/infer_session \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "timestamp": "2024-01-01T10:00:00",
        "user": "user123",
        "action": "login",
        "src_ip": "192.168.1.100"
      },
      {
        "timestamp": "2024-01-01T10:05:00",
        "user": "user123",
        "action": "file_download",
        "src_ip": "192.168.1.100"
      }
    ]
  }'
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py -v

# Generate coverage report
open htmlcov/index.html  # View coverage
```

---

## 🎓 Training Models

Train new models using the training package:

### XGBoost

```bash
python -m training.trainers.xgboost_trainer \
    --data data/processed/sessions.csv \
    --output models/xgb_v4 \
    --features 218
```

### LSTM

```bash
python -m training.trainers.lstm_trainer \
    --data data/processed/sessions.csv \
    --output models/lstm_v2 \
    --epochs 50 \
    --batch-size 64
```

### Attention LSTM

```bash
python -m training.trainers.attention_trainer \
    --data data/processed/sessions.csv \
    --output models/attn_v1 \
    --epochs 30
```

---

## 📊 Monitoring & Observability

### Logs

Structured logs with rotation (10MB per file, 5 backups):

```bash
# View real-time logs
tail -f logs/api.log

# Search for errors
grep ERROR logs/api.log

# View specific time range
grep "2024-10-12" logs/api.log
```

### Metrics

Prometheus-compatible metrics at `/metrics`:

- `inference_requests_total` - Total inference requests
- `inference_latency_seconds` - Response time histogram
- `alerts_total` - Alerts generated
- `cache_requests_total` - Cache hit/miss rate
- `active_requests` - Current concurrent requests

### Database

Query predictions stored in SQLite (or PostgreSQL):

```python
from app.core.database import get_recent_predictions, get_statistics

# Get last 10 predictions
predictions = get_recent_predictions(limit=10)

# Get aggregate statistics
stats = get_statistics()
print(f"Total predictions: {stats['total_predictions']}")
print(f"Alert rate: {stats['alert_rate']:.1%}")
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t insider-detect:2.0 .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  insider-detect:2.0

# Or use docker-compose
docker-compose up -d
```

---

## 🛠️ Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Code formatting
black app/ training/ tests/
isort app/ training/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ training/
```

---

## 📈 Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Precision** | 0.667 | 2 out of 3 alerts are real threats |
| **Recall** | 0.800 | Catches 80% of insider attacks |
| **F1-Score** | 0.727 | Balanced performance |
| **ROC-AUC** | 0.850 | Strong discriminatory power |
| **Latency** | <300ms | Real-time inference |
| **Throughput** | 100 req/min | Default rate limit |

---

## 🔒 Security Features

### Input Validation

All inputs validated with Pydantic models:
- Timestamp format checking
- String length limits
- IP address validation
- Max events per session (10,000)

### Rate Limiting

Default: 100 requests/minute per IP (configurable)

### Post-Filtering

Reduces false positives by:
- Filtering single-action sessions
- Suppressing short duration sessions
- Known benign pattern matching

---

## 🆕 What's New in v2.0

### Major Restructuring

- Consolidated 3 API files into 1
- Merged 3 training scripts into unified trainers
- Reorganized into `app/` and `training/` packages
- Removed duplicate and unnecessary files
- Archived old documentation (15 files moved)

### New Features

- Configuration management (YAML + .env)
- Structured logging with rotation
- Database persistence (SQLAlchemy)
- Prometheus metrics
- Session caching (5-min TTL)
- Model version management
- Comprehensive validation
- **New React Dashboard** for modern UI/UX
- **PowerShell Orchestration Script**

### Developer Experience

- Installable package (`pip install -e .`)
- Type hints throughout
- Unit tests with pytest
- Better error handling
- Cleaner imports
- Documentation overhaul
- **Orchestration script** (`scripts/run_everything.ps1`)

---

## 📅 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **2.0.0** | Oct 2025 | Major restructuring, new package layout, React dashboard, orchestration script |
| 1.0.0 | Jun 2025 | Initial release with hybrid ensemble |

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Format code (`black . && isort .`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

---

## 👥 Authors & Acknowledgments

**Development Team:**
- Insider Threat Detection Team

**Built With:**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [XGBoost](https://xgboost.ai/) - Gradient boosting
- [TensorFlow](https://www.tensorflow.org/) - Deep learning
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Prometheus](https://prometheus.io/) - Monitoring
- [React](https://react.dev/) - Frontend library
- [Vite](https://vitejs.dev/) - Frontend tooling
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

---

## 📞 Support & Contact

- **Documentation**: [docs/](docs/)
- **Bug Reports**: [GitHub Issues](https://github.com/Av7danger/insider-detect/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Av7danger/insider-detect/discussions)
- **Email**: support@example.com

---

## 🗺️ Roadmap

### Coming Soon
- [ ] Authentication & authorization (JWT)
- [ ] Kafka streaming integration
- [ ] Model explainability UI (SHAP/LIME)
- [ ] A/B testing framework

### Future Plans
- [ ] Additional ML models (Isolation Forest, Autoencoders)
- [ ] Data drift detection
- [ ] Mobile app
- [ ] Multi-tenancy support

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

---

**Made with ❤️ by the Insider Threat Detection Team**

*Last updated: October 16, 2025*
