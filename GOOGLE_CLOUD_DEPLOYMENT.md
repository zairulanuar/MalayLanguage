# Google Cloud Deployment Guide

This guide explains how to deploy the MalayLanguage MCP Server to Google Cloud Platform using the **proven, production-ready configuration** that successfully fixed all deployment issues.

## 🎯 Quick Start – Deploy in 5 Minutes

```bash
# 1. Clone the repository
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage

# 2. Add PyTorch (CPU version) to requirements.txt
echo -e "\n# PyTorch (CPU version)\n--extra-index-url https://download.pytorch.org/whl/cpu\ntorch>=2.0.0" >> requirements.txt

# 3. Deploy to Cloud Run
gcloud run deploy malaylanguage \
  --source . \
  --region asia-southeast3 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars PYTHONUNBUFFERED=1,MALAYA_CACHE=/tmp/.malaya

# 4. Get your live URL
gcloud run services describe malaylanguage \
  --region asia-southeast3 \
  --format 'value(status.url)'
```

**Your server is now live!** 🎉 Connect your MCP client using: `https://YOUR-URL.run.app/sse`

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
  - [Option 1: Cloud Run (Recommended)](#option-1-cloud-run-recommended-)
  - [Option 2: App Engine](#option-2-app-engine)
  - [Option 3: Cloud Build with GitHub Integration](#option-3-cloud-build-with-github-integration)
- [Configuration](#configuration)
- [Connecting Your App](#connecting-your-app)
- [Cost Estimates](#cost-estimates)
- [Management Commands](#management-commands)
- [Troubleshooting](#troubleshooting)
- [Known Issues & Fixes](#known-issues--fixes)
- [Security Best Practices](#security-best-practices)
- [Monitoring](#monitoring)

---

## Overview

Google Cloud Platform offers multiple ways to deploy containerized applications. This guide focuses on **Cloud Run** – the recommended, serverless option that automatically scales your MalayLanguage MCP server.

**What makes this guide different?**  
Every command and configuration here has been **tested and proven to work**. The common pitfalls (port misconfiguration, model download timeouts, permission errors) are already fixed.

---

## Prerequisites

- **Google Cloud Account**: [cloud.google.com](https://cloud.google.com)
- **Google Cloud Project**: Create one in the [GCP Console](https://console.cloud.google.com)
- **gcloud CLI**: [Install guide](https://cloud.google.com/sdk/docs/install)
- **Billing Enabled**: Required (free tier available)

### Initial Setup

```bash
# Install gcloud CLI (macOS)
brew install --cask google-cloud-sdk

# Or use the installer for other platforms
curl https://sdk.cloud.google.com | bash

# Initialize gcloud
gcloud init

# Login to your Google account
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## Deployment Options

### Option 1: Cloud Run (Recommended) ✅

Cloud Run is a fully managed serverless platform that automatically scales your container. **This is the production-tested option.**

**Advantages:**
- ✅ Automatic scaling to zero (pay only for usage)
- ✅ Free tier: 2 million requests/month
- ✅ No infrastructure management
- ✅ Fast deployment (~3-4 minutes)
- ✅ Global availability

#### Complete Deployment (With All Fixes)

```bash
# 1. Clone and enter directory
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage

# 2. CRITICAL: Add PyTorch dependency
echo -e "\n# PyTorch (CPU version)\n--extra-index-url https://download.pytorch.org/whl/cpu\ntorch>=2.0.0" >> requirements.txt

# 3. Deploy to Cloud Run
gcloud run deploy malaylanguage \
  --source . \
  --region asia-southeast3 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars PYTHONUNBUFFERED=1,MALAYA_CACHE=/tmp/.malaya

# 4. Get your service URL
SERVICE_URL=$(gcloud run services describe malaylanguage \
  --region asia-southeast3 \
  --format 'value(status.url)')
echo "Your service is live at: $SERVICE_URL"

# 5. Test it!
curl $SERVICE_URL/health
```

**Expected output:**
```json
{"status":"healthy","service":"malaylanguage-mcp-server","version":"1.0.0"}
```

#### Why These Settings?

| Setting | Value | Why |
|---------|-------|-----|
| `--memory` | `2Gi` | Malaya models require ~500MB + PyTorch overhead |
| `--cpu` | `1` | Sufficient for inference, can increase if needed |
| **No `--port` flag** | (omitted) | ❗ **CRITICAL**: Cloud Run injects `PORT` automatically |
| `MALAYA_CACHE` | `/tmp/.malaya` | Writable directory for non-root user |
| No `HOST` or `PORT` env vars | (omitted) | Your code reads `$PORT` and binds to `0.0.0.0` automatically |

#### Using the Pre-built Configuration

The repository includes a production-ready `cloudbuild.yaml` that:

- Uses **Artifact Registry** (not deprecated Container Registry)
- Pre-downloads models during build
- Sets correct permissions for non-root user
- Deploys automatically

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

#### Update Your Deployment

```bash
# Deploy new version (uses your latest code)
gcloud run deploy malaylanguage \
  --source . \
  --region asia-southeast3
```

---

### Option 2: App Engine

App Engine provides a managed platform with automatic scaling. Good for applications needing persistent storage or cron jobs.

**Note:** App Engine requires the same critical fixes (PyTorch, no hardcoded ports).

#### Deploy to App Engine

```bash
# Add PyTorch to requirements.txt
echo -e "\n# PyTorch (CPU version)\n--extra-index-url https://download.pytorch.org/whl/cpu\ntorch>=2.0.0" >> requirements.txt

# Deploy
gcloud app deploy app.yaml

# Get your app URL
gcloud app describe --format 'value(defaultHostname)'
```

Your app will be available at: `https://YOUR_PROJECT_ID.appspot.com`

**Important:** Your `app.yaml` should NOT specify port:

```yaml
# Correct app.yaml - NO port configuration
runtime: python311
entrypoint: python http_server.py

env_variables:
  MALAYA_CACHE: "/tmp/.malaya"
  PYTHONUNBUFFERED: "1"
  # DO NOT set HOST or PORT - your code handles this
```

---

### Option 3: Cloud Build with GitHub Integration

Automate deployments on every push to GitHub using Cloud Build triggers.

#### Setup Automated Deployment

**1. Connect GitHub Repository**

Go to **Cloud Build > Triggers** in GCP Console:
- Click "Connect Repository"
- Select "GitHub"
- Authenticate and select your repository
- Click "Connect"

**2. Create Build Trigger**

Via command line:
```bash
gcloud builds triggers create github \
  --repo-name=MalayLanguage \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

Or via Console:
- Click "Create Trigger"
- Name: `malaylanguage-deploy`
- Event: Push to branch
- Branch: `^main$`
- Configuration: Cloud Build configuration file
- Location: `cloudbuild.yaml`
- Click "Create"

**3. Trigger First Build**

```bash
# Manually trigger
gcloud builds submit --config cloudbuild.yaml

# Or push to GitHub main branch
git push origin main
```

Now **every push to `main` automatically deploys** to Cloud Run!

---

## Configuration

### Environment Variables

**✅ CORRECT (Production-tested):**

```bash
# Cloud Run - ONLY these two env vars are needed
gcloud run services update malaylanguage \
  --region asia-southeast3 \
  --set-env-vars "PYTHONUNBUFFERED=1,MALAYA_CACHE=/tmp/.malaya"
```

**❌ INCORRECT (Remove these):**
```bash
# DO NOT USE - These cause conflicts or are redundant
--set-env-vars "PORT=8080"        # Cloud Run injects this automatically
--set-env-vars "HOST=0.0.0.0"     # Your code already uses this default
```

### Available Variables

| Variable | Description | Default | Required? |
|---------|-------------|---------|-----------|
| `MALAYA_CACHE` | Model cache directory | `/tmp/.malaya` | ✅ Yes |
| `PYTHONUNBUFFERED` | Disable Python buffering | `1` | ✅ Yes |
| `PORT` | **DO NOT SET** - Cloud Run injects | `8080` | ❌ Never |
| `HOST` | **DO NOT SET** - Code defaults to `0.0.0.0` | `0.0.0.0` | ❌ Never |

### Memory and CPU Settings

**Recommended settings for production:**

```bash
gcloud run services update malaylanguage \
  --region asia-southeast3 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 900 \
  --concurrency 10
```

| Setting | Minimum | Recommended | Why |
|---------|---------|-------------|-----|
| Memory | 1Gi | **2Gi** | Models need ~500MB + PyTorch overhead |
| CPU | 1 | **1** | Sufficient for inference |
| Timeout | 300s | **900s** | Allow for cold start model loading |
| Concurrency | 1 | **10** | Balance performance and cost |

---

## Connecting Your App

After deployment, you'll have a public URL. Use it to configure your MCP client.

### Get Your Service URL

```bash
# Cloud Run
SERVICE_URL=$(gcloud run services describe malaylanguage \
  --region asia-southeast3 \
  --format 'value(status.url)')
echo $SERVICE_URL
# Example: https://malaylanguage-xxxxx-uc.a.run.app
```

### Configure MCP Client

**Claude Desktop:**

Edit your configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR-CLOUD-RUN-URL.run.app/sse",
      "transport": "sse"
    }
  }
}
```

**VS Code / Cursor:**

Create `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR-CLOUD-RUN-URL.run.app/sse",
      "transport": "sse",
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

### Test Your Deployment

```bash
# Health check
curl https://YOUR-URL.run.app/health

# Service info
curl https://YOUR-URL.run.app/

# Test SSE endpoint (should return 200)
curl -I https://YOUR-URL.run.app/sse

# Test a tool via HTTP
curl -X POST https://YOUR-URL.run.app/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"name": "detect_language", "arguments": {"text": "Selamat pagi"}}'
```

---

## Cost Estimates

### Cloud Run Pricing

**Free Tier (per month):**
- 2 million requests
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

**Paid Tier:**
- Requests: $0.40 per million
- Memory: $0.0000025 per GB-second
- CPU: $0.00001 per vCPU-second
- Networking: $0.12 per GB

**Example Usage:**
- 10,000 requests/month
- 2 GB memory, 1 vCPU
- Average 2s per request
- **Estimated Cost: FREE** (within free tier)

### Cloud Build Pricing

**Free Tier:**
- 120 build-minutes per day

**Paid Tier:**
- $0.003 per build-minute

**Example:**
- 1 build per day (~5 minutes)
- **Estimated Cost: FREE**

---

## Management Commands

### Cloud Run

```bash
# View logs
gcloud run logs read malaylanguage --region asia-southeast3

# Follow logs in real-time
gcloud run logs tail malaylanguage --region asia-southeast3

# List all services
gcloud run services list

# Get service details
gcloud run services describe malaylanguage --region asia-southeast3

# Delete service
gcloud run services delete malaylanguage --region asia-southeast3

# List revisions
gcloud run revisions list --service malaylanguage --region asia-southeast3

# Rollback to previous revision
gcloud run services update-traffic malaylanguage \
  --region asia-southeast3 \
  --to-revisions=malaylanguage-00001-xxx=100

# Set minimum instances (reduce cold starts)
gcloud run services update malaylanguage \
  --region asia-southeast3 \
  --min-instances 1
```

### Cloud Build

```bash
# List recent builds
gcloud builds list --limit 10

# Get build details
gcloud builds describe BUILD_ID

# View build logs
gcloud builds log BUILD_ID

# List triggers
gcloud builds triggers list

# Run trigger manually
gcloud builds triggers run TRIGGER_NAME --branch main
```

---

## Troubleshooting

### ❌ Deployment Fails: "Container failed to start on port 8080"

**Problem:** Your container isn't listening on the expected port.

**Solutions:**

✅ **Fix 1: Remove `--port` flag from deploy command**
```bash
# WRONG - causes conflict
gcloud run deploy ... --port 8080

# CORRECT - let Cloud Run inject PORT
gcloud run deploy ... # NO --port flag
```

✅ **Fix 2: Verify your http_server.py reads PORT**
```python
# CORRECT - your code should do this
port = int(os.environ.get("PORT", 8080))
uvicorn.run(app, host="0.0.0.0", port=port)
```

---

### ❌ Model Download Timeout

**Problem:** Deployment succeeds but container fails health check. Models are downloading at runtime and taking >4 minutes.

**Error in logs:**
```
Starting download of translation model...
Downloading: 100%|██████████| 500MB/500MB
... (container killed after 4 minutes)
```

**Solutions:**

✅ **Fix 1: Pre-download models in Dockerfile (PROVEN)**
```dockerfile
# Add this to your Dockerfile
RUN python -c "import malaya; \
    malaya.translation.huggingface(model='mesolitica/translation-t5-small-standard-bahasa-cased', force_check=True); \
    malaya.spelling_correction.transformer(model='mesolitica/bert-tiny-standard-bahasa-cased', force_check=True); \
    malaya.normalizer.transformer(model='mesolitica/normalizer-t5-small-standard-bahasa-cased', force_check=True)"
```

✅ **Fix 2: Add PyTorch to requirements.txt (REQUIRED)**
```txt
# CRITICAL - Malaya needs PyTorch
--extra-index-url https://download.pytorch.org/whl/cpu
torch>=2.0.0
```

✅ **Fix 3: Increase memory and timeout**
```bash
gcloud run services update malaylanguage \
  --memory 2Gi \
  --timeout 900 \
  --region asia-southeast3
```

---

### ❌ Permission Denied: Cannot write to /tmp/.malaya

**Problem:** Container runs as non-root but cache directory is owned by root.

**Error in logs:**
```
PermissionError: [Errno 13] Permission denied: '/tmp/.malaya'
```

**Solution:** Fix permissions in Dockerfile
```dockerfile
# Create directory and set permissions
RUN mkdir -p /tmp/.malaya && \
    chmod 777 /tmp/.malaya

# Create non-root user and own the directory
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /tmp/.malaya
USER appuser
```

---

### ❌ Build Fails: "Invalid requirement"

**Problem:** Syntax error in `requirements.txt`

**Error:**
```
ERROR: Invalid requirement: 'ruff>=0.1.0# Core dependencies'
```

**Solution:** Comments must be on their own line
```txt
# CORRECT
ruff>=0.1.0

# WRONG - comment attached to package line
ruff>=0.1.0# Core dependencies
```

---

### ❌ pip install Fails: Can't find torch

**Problem:** PyTorch download times out or fails

**Solution:** Use CPU-only index and retry
```bash
# Add this to requirements.txt
--extra-index-url https://download.pytorch.org/whl/cpu
torch>=2.0.0
```

---

### ❌ Service Not Accessible

**Problem:** Cannot reach your deployed service

**Solutions:**

1. **Check if service allows unauthenticated access:**
```bash
gcloud run services add-iam-policy-binding malaylanguage \
  --region asia-southeast3 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

2. **Verify service is running:**
```bash
gcloud run services describe malaylanguage --region asia-southeast3
```

3. **Check logs for errors:**
```bash
gcloud run logs read malaylanguage --region asia-southeast3
```

---

### ❌ Cold Start Too Slow

**Problem:** First request takes 30-90 seconds

**Explanation:** Cloud Run scales to zero. The first request starts a new instance and loads ML models from cache (not downloading, but still loading into memory).

**Solutions:**

✅ **Keep one instance warm:**
```bash
gcloud run services update malaylanguage \
  --region asia-southeast3 \
  --min-instances 1
```
Cost: ~$4-5/month for always-on instance

✅ **Increase CPU for faster loading:**
```bash
gcloud run services update malaylanguage \
  --region asia-southeast3 \
  --cpu 2
```

✅ **Set up keep-alive pings:**
```bash
gcloud scheduler jobs create http malaylanguage-keepalive \
  --schedule="*/4 * * * *" \
  --uri="$(gcloud run services describe malaylanguage --region asia-southeast3 --format='value(status.url)')/health" \
  --http-method=GET \
  --location=asia-southeast3
```

---

## Known Issues & Fixes

This section documents issues **encountered and solved** during production deployment.

| Issue | Symptom | Root Cause | Fix |
|-------|---------|------------|-----|
| **Port conflict** | `Container failed to start on port 8080` | `--port` flag overrides Cloud Run's PORT injection | **Remove `--port` from deploy command** |
| **Model timeout** | Health check fails, container killed | Models download at runtime (takes 4+ minutes) | **Pre-download models in Dockerfile** |
| **PyTorch missing** | Model pre-download fails | Malaya requires PyTorch | **Add torch to requirements.txt** |
| **Cache permission** | `Permission denied: /tmp/.malaya` | Non-root user can't write to root-owned dir | **chmod 777 and chown to appuser** |
| **Syntax error** | `Invalid requirement: 'ruff>=0.1.0# Core'` | Comment attached to package line | **Comments on separate lines** |
| **Wrong registry** | Deployment fails with image not found | Using gcr.io instead of Artifact Registry | **Use $_REGION-docker.pkg.dev** |

**All these issues are fixed in the current repository.** Use the provided `Dockerfile`, `cloudbuild.yaml`, and this guide to avoid them.

---

## Security Best Practices

### ✅ Recommended for Production

1. **Use non-root user** (already in Dockerfile)
2. **Enable Cloud Armor** for DDoS protection
3. **Use Secret Manager** for API keys
4. **Set up VPC Service Controls** for network security
5. **Enable Cloud Monitoring** alerts
6. **Regularly update dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

### 🔐 IAM Roles (Minimal Required)

| Service Account | Required Roles |
|-----------------|----------------|
| Cloud Build | `roles/run.builder`, `roles/iam.serviceAccountUser` |
| Cloud Run | `roles/run.invoker` (for public access) |
| Your User | `roles/run.admin`, `roles/iam.serviceAccountUser` |

---

## Monitoring

### View Metrics in Console

```bash
# Get service URL then open in browser
gcloud run services describe malaylanguage \
  --region asia-southeast3 \
  --format 'value(status.url)'
```

Visit: `https://console.cloud.google.com/run`

### Set Up Alerts

```bash
# Example: Alert on 5% error rate for 5 minutes
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="MalayLanguage High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="malaylanguage"' \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### Logs Explorer Queries

**View startup errors:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="malaylanguage"
severity>=ERROR
"Traceback"
```

**View model loading time:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="malaylanguage"
textPayload:"Downloading"
```

**View health check failures:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="malaylanguage"
httpRequest.status=503 OR httpRequest.status=500
```

---

## Summary: What Makes This Deployment Work

| Component | Critical Requirement | Status in This Guide |
|-----------|---------------------|---------------------|
| **Port** | No `--port` flag, read `$PORT` env var | ✅ CORRECT |
| **Host** | Bind to `0.0.0.0`, not `127.0.0.1` | ✅ CORRECT |
| **User** | Non-root user with UID 1000 | ✅ CORRECT |
| **Cache** | Writable `/tmp/.malaya` with `chmod 777` | ✅ CORRECT |
| **Models** | Pre-downloaded during build | ✅ CORRECT |
| **PyTorch** | Added to requirements.txt with CPU index | ✅ CORRECT |
| **Registry** | Artifact Registry (`*-docker.pkg.dev`) | ✅ CORRECT |
| **Memory** | 2Gi minimum for model loading | ✅ CORRECT |
| **Timeout** | 900s for cold start | ✅ CORRECT |

---

## Next Steps

- ✅ **Deploy your service** using the commands above
- ✅ **Get your service URL** and test the health endpoint
- ✅ **Configure your MCP client** with the SSE endpoint
- ✅ **Test the connection** with sample Malay text
- ✅ **Set up monitoring** and error alerts
- ⬜ **Configure custom domain** (optional)
- ⬜ **Set up CI/CD** with Cloud Build triggers
- ⬜ **Add load testing** for production scale

---

## Support & Resources

- **GitHub Issues**: [https://github.com/zairulanuar/MalayLanguage/issues](https://github.com/zairulanuar/MalayLanguage/issues)
- **Malaya Documentation**: [https://malaya.readthedocs.io/](https://malaya.readthedocs.io/)
- **Cloud Run Docs**: [https://cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **GCP Status**: [https://status.cloud.google.com/](https://status.cloud.google.com/)

---

**This guide is production-tested.** Every command and configuration has been verified to work with the MalayLanguage MCP server on Google Cloud Run. If you encounter any issues not covered here, please open a GitHub issue.
