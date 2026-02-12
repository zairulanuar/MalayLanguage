# Cloud Run Error Fixes

**Date:** February 12, 2026  
**Status:** ✅ Fixed

## Summary

Found and fixed **2 critical configuration errors** that would cause Cloud Run deployment failures:

1. **Port Configuration Mismatch**
2. **Model Cache Directory Permissions Issue**

---

## Error #1: Port Configuration Mismatch

### Problem
The application was configured to use different ports across different deployment configurations:
- **Dockerfile**: `PORT=8080`, `EXPOSE 8080`
- **cloudbuild.yaml**: `--port 8080`
- **app.yaml**: ❌ **Missing PORT environment variable** (would default to 8000)
- **http_server.py**: Defaults to `8000` if `PORT` env var not set

### Root Cause
When deploying to Cloud Run via App Engine (using `app.yaml`), the environment variables were not explicitly specified, causing the HTTP server to listen on port 8000 instead of the expected 8080. Cloud Run would expect traffic on port 8080 but the application would be listening on 8000, resulting in connection failures.

### Solution
Added explicit environment variables to `app.yaml`:

```yaml
env_variables:
  PYTHONUNBUFFERED: "1"
  MALAYA_CACHE: "/tmp/.malaya"
  PORT: "8080"          # ✅ ADDED
  HOST: "0.0.0.0"       # ✅ ADDED
```

### Files Modified
- ✅ [app.yaml](app.yaml)

---

## Error #2: Model Cache Directory Permissions

### Problem
The Dockerfile was using `/root/.malaya` for the model cache directory:

```dockerfile
RUN mkdir -p /root/.malaya
ENV MALAYA_CACHE=/root/.malaya
```

However:
- **cloudbuild.yaml** correctly uses: `MALAYA_CACHE=/tmp/.malaya`
- **app.yaml** correctly uses: `MALAYA_CACHE="/tmp/.malaya"`
- **Dockerfile.hf** (Hugging Face) correctly uses: `MALAYA_CACHE=/tmp/.malaya`

### Root Cause
Cloud Run containers often run as unprivileged users and don't have write permissions to `/root`. This would cause runtime failures when the Malaya library tries to cache downloaded models.

The `/root` directory is typically write-protected in containerized environments, while `/tmp` is guaranteed to be writable.

### Solution
Updated Dockerfile to use `/tmp/.malaya`:

```dockerfile
RUN mkdir -p /tmp/.malaya
ENV MALAYA_CACHE=/tmp/.malaya
```

### Files Modified
- ✅ [Dockerfile](Dockerfile)

---

## Configuration Consistency Matrix

| Configuration | PORT | MALAYA_CACHE | Status |
|---|---|---|---|
| **Dockerfile** | 8080 | /tmp/.malaya | ✅ Fixed |
| **Dockerfile.hf** | 7860 | /tmp/.malaya | ✅ OK |
| **app.yaml** | 8080 | /tmp/.malaya | ✅ Fixed |
| **cloudbuild.yaml** | 8080 | /tmp/.malaya | ✅ OK |

---

## Deployment Methods Affected

### ✅ Cloud Build (cloudbuild.yaml)
- Already correctly configured
- No changes needed

### ✅ App Engine (app.yaml)
- **Status**: FIXED
- Now includes explicit PORT and HOST variables

### ✅ Cloud Run (gcloud CLI)
- If using `gcloud run deploy` directly with environment variables, now consistent with app.yaml

### ✅ Hugging Face Spaces (Dockerfile.hf)
- Already correctly configured
- Uses port 7860 (HF Spaces default)

---

## Testing the Fixes

### 1. Local Testing with Docker

```bash
# Build the image
docker build -t malaylanguage-mcp:test .

# Run with Cloud Run environment variables
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  -e MALAYA_CACHE=/tmp/.malaya \
  -e PYTHONUNBUFFERED=1 \
  malaylanguage-mcp:test

# Test the health endpoint
curl http://localhost:8080/health
```

### 2. Cloud Build Deployment

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

### 3. App Engine Deployment

```bash
gcloud app deploy app.yaml --project=YOUR_PROJECT_ID
```

### 4. Verify Deployment

```bash
# Check Cloud Run service
gcloud run services describe malaylanguage-mcp \
  --region us-central1 \
  --project=YOUR_PROJECT_ID

# Test health endpoint
curl https://your-cloud-run-url.run.app/health
```

---

## Potential Cloud Run Issues to Monitor

### Cold Start Times
- **Expected**: 30-90 seconds (first request loads ML models)
- **Solution**: Use min-instances or keep-alive scheduler (see GOOGLE_CLOUD_DEPLOYMENT.md)

### Memory Usage
- **Current allocation**: 2Gi (from cloudbuild.yaml)
- **Minimum recommended**: 2Gi (models require ~1.5Gi+)
- **Maximum**: 4Gi (if budget allows)

### Timeout Issues
- **Default Cloud Run timeout**: 3600 seconds (1 hour)
- **Model loading timeout**: Typically < 60 seconds
- **Request timeout**: Depends on text processing load

---

## Best Practices for Cloud Run Deployments

✅ **Always use**:
- Environment variables (not hardcoded values)
- `/tmp` for temporary data (writable, ephemeral)
- Explicit port numbers matching across all configs
- Health check endpoints for monitoring
- Comprehensive logging

❌ **Never use**:
- `/root` for writable data
- Port mismatches between configs
- Hardcoded paths or ports
- Local filesystem for persistent data (use Cloud Storage instead)

---

## Files Changed Summary

```
modified:   Dockerfile       (MALAYA_CACHE: /root/.malaya → /tmp/.malaya)
modified:   app.yaml         (Added: PORT=8080, HOST=0.0.0.0)
```

## Verification

To verify all configurations are consistent:

```bash
# Check Dockerfile
grep -i "MALAYA_CACHE\|PORT" Dockerfile

# Check app.yaml
grep -i "MALAYA_CACHE\|PORT" app.yaml

# Check cloudbuild.yaml
grep -i "MALAYA_CACHE\|PORT" cloudbuild.yaml
```

All three should show:
- `MALAYA_CACHE=/tmp/.malaya` ✅
- `PORT=8080` ✅

---

## Next Steps

1. ✅ Commit these fixes
2. ✅ Test locally with Docker
3. ✅ Deploy to Cloud Build/Cloud Run
4. ✅ Monitor logs for startup issues
5. ✅ Verify health endpoint responds with 200 OK
6. ✅ Test SSE connection from MCP client

