# Requirements Files Guide

## 📦 Two Requirements Files Strategy

We maintain **two separate requirements files** for better dependency management:

### 1. `requirements.txt` - Development Environment

**Purpose**: For local development and testing

**Includes**:
- ✅ All runtime dependencies
- ✅ Database dependencies (SQLAlchemy, alembic, psycopg2-binary)
- ✅ Development tools (pytest, black, flake8)
- ✅ Production server (gunicorn)

**Use when**:
```bash
# Local development
pip install -r requirements.txt

# Testing
pytest

# Code formatting
black .
flake8 .
```

---

### 2. `requirements-prod.txt` - Production Environment

**Purpose**: For production deployment (Render, AWS, etc.)

**Includes**:
- ✅ All runtime dependencies
- ✅ Database dependencies (SQLAlchemy, alembic, psycopg2-binary)
- ✅ Production server (gunicorn)
- ❌ **No development tools** (pytest, black, flake8)

**Use when**:
```bash
# Production deployment
pip install -r requirements-prod.txt

# Docker production image
RUN pip install -r requirements-prod.txt
```

---

## 🎯 Key Differences

| Dependency | requirements.txt | requirements-prod.txt | Why? |
|------------|------------------|----------------------|------|
| **fastapi** | ✅ 0.115.5 | ✅ 0.115.5 | Runtime - needed |
| **SQLAlchemy** | ✅ 2.0.36 | ✅ 2.0.36 | Runtime - needed |
| **gunicorn** | ✅ 23.0.0 | ✅ 23.0.0 | Production server - needed |
| **pytest** | ✅ 8.3.3 | ❌ Not included | Dev only |
| **black** | ✅ 24.8.0 | ❌ Not included | Dev only |
| **flake8** | ✅ 7.1.1 | ❌ Not included | Dev only |

---

## 🔄 Version Synchronization

Both files use the **same versions** for shared dependencies:

✅ **Synchronized**:
- fastapi==0.115.5
- SQLAlchemy==2.0.36
- langgraph==0.2.34
- All runtime dependencies match

This ensures:
- ✅ Development environment matches production
- ✅ No surprises when deploying
- ✅ Consistent behavior across environments

---

## 🚀 Deployment Guide

### Local Development:
```bash
# Install all dependencies including dev tools
pip install -r requirements.txt

# Run tests
pytest

# Format code
black src/
```

### Production (Render/AWS):
```bash
# Install only production dependencies
pip install -r requirements-prod.txt

# Start server
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker:
```dockerfile
# Use production requirements for smaller image
FROM python:3.11-slim

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY . .
CMD ["gunicorn", "main:app", "--workers", "4"]
```

---

## 📊 Size Comparison

| File | Lines | Size | Use Case |
|------|-------|------|----------|
| **requirements.txt** | 58 | Larger | Development |
| **requirements-prod.txt** | 46 | Smaller | Production |

**Production benefits**:
- ⚡ Faster install (fewer packages)
- 💾 Smaller Docker images
- 🔒 Fewer attack vectors (no dev tools)

---

## 🔧 Maintenance

### When updating dependencies:

1. **Update both files** with the same runtime versions
2. **Keep dev tools** only in requirements.txt
3. **Test both**:
   ```bash
   # Test production requirements
   pip install -r requirements-prod.txt
   python -c "import fastapi; import sqlalchemy; print('OK')"

   # Test development requirements
   pip install -r requirements.txt
   pytest
   ```

---

## 💡 Best Practices

### ✅ DO:
- Keep runtime dependencies synchronized
- Use requirements-prod.txt in production
- Test both files regularly
- Update versions together

### ❌ DON'T:
- Don't use requirements.txt in production (unnecessary dev tools)
- Don't have different runtime versions between files
- Don't forget to add database dependencies to both

---

## 🎯 Quick Reference

**I'm a developer**:
→ Use `requirements.txt`

**I'm deploying to production**:
→ Use `requirements-prod.txt`

**I'm setting up CI/CD**:
→ Use `requirements-prod.txt` for deployment
→ Use `requirements.txt` for testing

**I'm building a Docker image**:
→ Use `requirements-prod.txt` for smaller images

---

## 📝 Example: Render Deployment

In your `render.yaml`:
```yaml
services:
  - type: web
    name: vds-backend
    env: python
    buildCommand: pip install -r requirements-prod.txt
    startCommand: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

**Last Updated**: October 30, 2025
**Maintained By**: VDS Team
