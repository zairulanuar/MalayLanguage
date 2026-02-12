# Cloud Build Troubleshooting Guide

This guide helps you diagnose and fix Google Cloud Build failures for the MalayLanguage MCP Server.

## How to Access Cloud Build Logs

### Method 1: Google Cloud Console (Web UI)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to **Cloud Build** > **History**
4. Click on the failed build to see detailed logs
5. Look for error messages in the build steps

### Method 2: Using gcloud CLI

```bash
# List recent builds
gcloud builds list --limit 10

# Get details of a specific build
gcloud builds describe BUILD_ID

# View logs for a specific build
gcloud builds log BUILD_ID

# Stream logs in real-time during a build
gcloud builds submit --config cloudbuild.yaml --stream-logs
```

### Method 3: Direct URL

If you have a Cloud Build URL like:
```
https://console.cloud.google.com/cloud-build/builds;region=global/BUILD_ID?project=PROJECT_ID
```

Simply open it in your browser while logged into your Google Cloud account.

## Common Cloud Build Failures and Solutions

### 1. Container Failed to Start (Most Common)

**Error Message:**
```
The user-provided container failed to start and listen on the port defined by the PORT environment variable
```

**Causes:**
- App not listening on the PORT environment variable
- App binding to `127.0.0.1` instead of `0.0.0.0`
- App crashing on startup

**Solution:**
1. Check that `http_server.py` reads the `PORT` environment variable:
   ```python
   port = int(os.getenv("PORT", "8000"))
   ```

2. Verify the app binds to `0.0.0.0`:
   ```python
   uvicorn.run(http_app, host="0.0.0.0", port=port)
   ```

3. Check `cloudbuild.yaml` sets the correct port:
   ```yaml
   --port '8080'
   --set-env-vars 'PORT=8080,HOST=0.0.0.0,...'
   ```

4. Test locally with the same port:
   ```bash
   docker build -t test -f Dockerfile .
   docker run -p 8080:8080 -e PORT=8080 -e HOST=0.0.0.0 test
   curl http://localhost:8080/health
   ```

### 2. Build Timeout

**Error Message:**
```
Build timed out
```

**Solution:**
1. Increase build timeout in `cloudbuild.yaml`:
   ```yaml
   options:
     machineType: 'E2_HIGHCPU_4'
     logging: CLOUD_LOGGING_ONLY
   timeout: 1200s  # 20 minutes
   ```

2. Or when submitting manually:
   ```bash
   gcloud builds submit --config cloudbuild.yaml --timeout=20m
   ```

### 3. Permission Errors

**Error Message:**
```
Missing necessary permission iam.serviceAccounts.actAs
```
or
```
PermissionDenied: Permission 'run.services.create' denied
```

**Solution:**
1. Grant necessary roles to the Cloud Build service account:
   ```bash
   PROJECT_ID=$(gcloud config get-value project)
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   
   # Grant Cloud Run Admin role
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
     --role="roles/run.admin"
   
   # Grant Service Account User role
   gcloud iam service-accounts add-iam-policy-binding \
     $PROJECT_NUMBER-compute@developer.gserviceaccount.com \
     --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   ```

### 4. Docker Build Failures

**Error Message:**
```
failed to solve with frontend dockerfile.v0
```
or
```
COPY failed: file not found
```

**Causes:**
- Files excluded by `.dockerignore` or `.gcloudignore`
- Incorrect file paths in Dockerfile
- Missing dependencies

**Solution:**
1. Check `.gcloudignore` doesn't exclude required files:
   ```bash
   # server.py, http_server.py, server.json must NOT be in .gcloudignore
   cat .gcloudignore | grep -E "server.py|http_server.py|server.json"
   ```

2. Verify Dockerfile paths are correct:
   ```dockerfile
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY server.py .
   COPY http_server.py .
   COPY server.json .
   ```

3. Test build locally:
   ```bash
   docker build -t test -f Dockerfile .
   ```

### 5. Out of Memory During Build

**Error Message:**
```
The build exceeded the memory limit
```

**Solution:**
1. Use a larger machine type in `cloudbuild.yaml`:
   ```yaml
   options:
     machineType: 'E2_HIGHCPU_8'  # More powerful machine
     logging: CLOUD_LOGGING_ONLY
   ```

2. Available machine types:
   - `E2_HIGHCPU_4` (4 vCPU, 4 GB) - default, cost-efficient
   - `E2_HIGHCPU_8` (8 vCPU, 8 GB) - for larger builds
   - `N1_HIGHCPU_8` (8 vCPU, 7.2 GB) - alternative
   - `N1_HIGHCPU_32` (32 vCPU, 28.8 GB) - for very large builds

### 6. API Not Enabled

**Error Message:**
```
API [run.googleapis.com] not enabled on project
```

**Solution:**
```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 7. Deployment Succeeds But Service Doesn't Respond

**Error Message:**
```
Service returns 502 Bad Gateway or 503 Service Unavailable
```

**Causes:**
- App crashes after deployment
- App takes too long to start
- Wrong port configuration

**Solution:**
1. Check Cloud Run logs:
   ```bash
   gcloud run logs read malaylanguage-mcp --region us-central1 --limit 50
   ```

2. Test the health endpoint:
   ```bash
   # Get the service URL
   URL=$(gcloud run services describe malaylanguage-mcp \
     --region us-central1 \
     --format 'value(status.url)')
   
   # Test health endpoint
   curl $URL/health
   ```

3. Increase startup timeout in `cloudbuild.yaml`:
   ```yaml
   - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
     entrypoint: gcloud
     args:
       - 'run'
       - 'deploy'
       - 'malaylanguage-mcp'
       # ... other args ...
       - '--timeout'
       - '300'  # 5 minutes startup timeout
   ```

## Debugging Steps

### Step 1: Verify Local Build Works

```bash
# Build Docker image
docker build -t malaylanguage-test -f Dockerfile .

# Run container with Cloud Run environment variables
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  -e PYTHONUNBUFFERED=1 \
  -e MALAYA_CACHE=/tmp/.malaya \
  malaylanguage-test

# Test in another terminal
curl http://localhost:8080/health
curl http://localhost:8080/
```

### Step 2: Check Build Configuration

```bash
# Verify cloudbuild.yaml is valid YAML
cat cloudbuild.yaml | python -c "import sys, yaml; yaml.safe_load(sys.stdin)"

# Check environment variables match
grep -A 5 "set-env-vars" cloudbuild.yaml
```

### Step 3: Test Manual Cloud Build Submission

```bash
# Submit build manually to see real-time logs
gcloud builds submit \
  --config cloudbuild.yaml \
  --stream-logs
```

### Step 4: Check Deployed Service

```bash
# Get service status
gcloud run services describe malaylanguage-mcp \
  --region us-central1 \
  --format json

# Check recent logs
gcloud run logs read malaylanguage-mcp \
  --region us-central1 \
  --limit 100
```

## Configuration Checklist

- [ ] `Dockerfile` exposes correct port (8080)
- [ ] `Dockerfile` sets `ENV PORT=8080`
- [ ] `http_server.py` reads `PORT` from environment
- [ ] `http_server.py` binds to `0.0.0.0`
- [ ] `cloudbuild.yaml` deploys with `--port 8080`
- [ ] `cloudbuild.yaml` sets `PORT=8080` in environment
- [ ] `.gcloudignore` doesn't exclude required files
- [ ] Required APIs are enabled
- [ ] Service account has necessary permissions
- [ ] Local Docker build succeeds
- [ ] Local Docker run responds to health check

## Getting More Help

If you're still experiencing issues:

1. **Copy the full error message** from Cloud Build logs
2. **Check the specific build step** that failed
3. **Look for stack traces** in the logs
4. **Test the exact same configuration locally**
5. **Open an issue** with:
   - Build ID
   - Full error message
   - Output of `docker build` locally
   - Your `cloudbuild.yaml` configuration

## Related Documentation

- [GOOGLE_CLOUD_DEPLOYMENT.md](./GOOGLE_CLOUD_DEPLOYMENT.md) - Full deployment guide
- [Dockerfile](./Dockerfile) - Container configuration
- [cloudbuild.yaml](./cloudbuild.yaml) - Build configuration
- [Google Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
