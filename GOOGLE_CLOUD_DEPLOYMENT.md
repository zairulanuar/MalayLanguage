# Google Cloud Deployment Guide

This guide explains how to deploy the MalayLanguage MCP Server to Google Cloud Platform.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
  - [Option 1: Cloud Run (Recommended)](#option-1-cloud-run-recommended)
  - [Option 2: App Engine](#option-2-app-engine)
  - [Option 3: Cloud Build with GitHub Integration](#option-3-cloud-build-with-github-integration)
- [Configuration](#configuration)
- [Connecting Your App](#connecting-your-app)
- [Cost Estimates](#cost-estimates)
- [Troubleshooting](#troubleshooting)

---

## Overview

Google Cloud Platform offers multiple ways to deploy containerized applications:

- **Cloud Run** (Recommended): Serverless container platform with automatic scaling
- **App Engine**: Managed platform service with automatic scaling
- **Cloud Build**: CI/CD pipeline for automated deployments

All options support the existing Dockerfile and require minimal configuration.

---

## Prerequisites

1. **Google Cloud Account**: Create one at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud Project**: Create a new project in the [GCP Console](https://console.cloud.google.com)
3. **gcloud CLI**: Install from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
4. **Billing Enabled**: Required for deployment (free tier available)

### Initial Setup

```bash
# Install gcloud CLI (macOS example)
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
```

---

## Deployment Options

### Option 1: Cloud Run (Recommended)

Cloud Run is a fully managed serverless platform that automatically scales your container. Best for production deployments.

**Advantages:**
- ✅ Automatic scaling to zero (pay only for usage)
- ✅ Free tier: 2 million requests/month
- ✅ No infrastructure management
- ✅ Fast deployment (~2-3 minutes)
- ✅ Global availability

#### Quick Deploy

```bash
# Clone the repository
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage

# Deploy to Cloud Run (one command!)
gcloud run deploy malaylanguage-mcp \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars PYTHONUNBUFFERED=1,PORT=8000,HOST=0.0.0.0
```

This command will:
1. Build the Docker image from your Dockerfile
2. Push it to Google Container Registry
3. Deploy it to Cloud Run
4. Return a public URL like: `https://malaylanguage-mcp-XXXXX-uc.a.run.app`

#### Using Pre-built Configuration

Alternatively, use the provided `cloudbuild.yaml`:

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# The deployment happens automatically
```

#### Get Your Service URL

```bash
gcloud run services describe malaylanguage-mcp \
  --region us-central1 \
  --format 'value(status.url)'
```

#### Update Deployment

```bash
# Deploy new version
gcloud run deploy malaylanguage-mcp \
  --source . \
  --region us-central1
```

---

### Option 2: App Engine

App Engine provides a managed platform with automatic scaling. Good for applications needing persistent storage or cron jobs.

**Advantages:**
- ✅ Free tier available
- ✅ Automatic scaling
- ✅ Built-in services (cron, task queues)
- ✅ Simple deployment

#### Deploy to App Engine

```bash
# Create app.yaml (already provided in repository)
# Then deploy
gcloud app deploy app.yaml

# Get your app URL
gcloud app describe --format 'value(defaultHostname)'
```

Your app will be available at: `https://YOUR_PROJECT_ID.appspot.com`

#### View Logs

```bash
gcloud app logs tail -s default
```

#### Update Deployment

```bash
# Deploy new version
gcloud app deploy app.yaml

# Or deploy without promoting (for testing)
gcloud app deploy app.yaml --no-promote --version test
```

---

### Option 3: Cloud Build with GitHub Integration

Automate deployments on every push to GitHub using Cloud Build triggers.

#### Setup Automated Deployment

1. **Connect GitHub Repository**

   Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers) in GCP Console:
   - Click "Connect Repository"
   - Select "GitHub"
   - Authenticate and select your repository
   - Click "Connect"

2. **Create Build Trigger**

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

3. **Trigger First Build**

   ```bash
   # Manually trigger build
   gcloud builds submit --config cloudbuild.yaml

   # Or push to GitHub main branch
   git push origin main
   ```

Now every push to the `main` branch automatically deploys to Cloud Run!

---

## Configuration

### Environment Variables

Set environment variables for your deployment:

**Cloud Run:**
```bash
gcloud run services update malaylanguage-mcp \
  --set-env-vars "HOST=0.0.0.0,PORT=8000,MALAYA_CACHE=/tmp/.malaya"
```

**App Engine:**
Add to `app.yaml`:
```yaml
env_variables:
  HOST: "0.0.0.0"
  PORT: "8000"
  MALAYA_CACHE: "/tmp/.malaya"
```

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `MALAYA_CACHE` | Model cache directory | `~/.malaya` |
| `PYTHONUNBUFFERED` | Disable Python buffering | `1` |

### Memory and CPU Settings

**Cloud Run:**
```bash
gcloud run services update malaylanguage-mcp \
  --memory 2Gi \
  --cpu 2
```

**Recommended Settings:**
- Memory: 1-2 GB (models are ~500MB)
- CPU: 1-2 vCPUs
- Timeout: 300s (for model loading)

---

## Connecting Your App

After deployment, you'll have a public URL. Use it to configure your MCP client.

### Get Your Service URL

**Cloud Run:**
```bash
gcloud run services describe malaylanguage-mcp \
  --region us-central1 \
  --format 'value(status.url)'
```

**App Engine:**
```bash
gcloud app describe --format 'value(defaultHostname)'
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
      "url": "https://your-cloud-run-url.run.app/sse",
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
      "url": "https://your-cloud-run-url.run.app/sse",
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
curl https://your-cloud-run-url.run.app/health

# Should return:
# {"status":"healthy","service":"malaylanguage-mcp-server","version":"1.0.0"}

# Service info
curl https://your-cloud-run-url.run.app/

# Test SSE endpoint
curl https://your-cloud-run-url.run.app/sse
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
- 1 GB memory, 1 vCPU
- Average 2s per request
- **Estimated Cost: FREE** (within free tier)

### App Engine Pricing

**Free Tier (per day):**
- 28 instance hours
- 1 GB outbound data

**Standard Environment:**
- Instance: $0.05 - $0.20 per hour (varies by instance class)
- Outbound data: $0.12 per GB

**Example Usage:**
- F1 instance (256MB, 600MHz)
- 10 hours/day active
- **Estimated Cost: FREE** (within free tier for light usage)

### Cloud Build Pricing

**Free Tier (per day):**
- 120 build-minutes

**Paid Tier:**
- $0.003 per build-minute

**Example Usage:**
- 1 build per day (~5 minutes)
- **Estimated Cost: FREE** (within free tier)

---

## Management Commands

### Cloud Run

```bash
# View logs
gcloud run logs read malaylanguage-mcp --region us-central1

# Follow logs
gcloud run logs tail malaylanguage-mcp --region us-central1

# List services
gcloud run services list

# Get service details
gcloud run services describe malaylanguage-mcp --region us-central1

# Delete service
gcloud run services delete malaylanguage-mcp --region us-central1

# List revisions
gcloud run revisions list --service malaylanguage-mcp

# Rollback to previous revision
gcloud run services update-traffic malaylanguage-mcp \
  --to-revisions REVISION_NAME=100
```

### App Engine

```bash
# View logs
gcloud app logs tail

# List versions
gcloud app versions list

# Stop a version
gcloud app versions stop VERSION_ID

# Delete old versions
gcloud app versions delete VERSION_ID

# Set traffic split
gcloud app services set-traffic default \
  --splits v1=50,v2=50
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
gcloud builds triggers run TRIGGER_NAME
```

---

## Troubleshooting

### Deployment Fails

**Problem**: Build or deployment fails

**Solutions:**
1. Check build logs: `gcloud builds list --limit 1`
2. Verify APIs are enabled:
   ```bash
   gcloud services list --enabled
   ```
3. Check IAM permissions: Ensure service account has required roles
4. Verify Dockerfile builds locally:
   ```bash
   docker build -t test .
   docker run -p 8000:8000 test python http_server.py
   ```

### Service Not Accessible

**Problem**: Cannot access the deployed service

**Solutions:**
1. Check service status:
   ```bash
   gcloud run services describe malaylanguage-mcp --region us-central1
   ```
2. Verify service allows unauthenticated requests:
   ```bash
   gcloud run services add-iam-policy-binding malaylanguage-mcp \
     --region us-central1 \
     --member="allUsers" \
     --role="roles/run.invoker"
   ```
3. Test health endpoint: `curl https://your-url/health`

### Cold Start Issues

**Problem**: First request is slow (30-90 seconds)

**Explanation**: Cloud Run scales to zero. First request starts a new instance and loads ML models.

**Solutions:**
1. Set minimum instances:
   ```bash
   gcloud run services update malaylanguage-mcp \
     --min-instances 1 \
     --region us-central1
   ```
2. Use Cloud Scheduler for keep-alive pings:
   ```bash
   gcloud scheduler jobs create http malaylanguage-keepalive \
     --schedule="*/5 * * * *" \
     --uri="https://your-url/health" \
     --http-method=GET
   ```
3. Increase CPU/memory for faster startup

### Out of Memory

**Problem**: Service crashes with memory errors

**Solutions:**
1. Increase memory allocation:
   ```bash
   gcloud run services update malaylanguage-mcp \
     --memory 2Gi \
     --region us-central1
   ```
2. Check logs for specific issues:
   ```bash
   gcloud run logs read malaylanguage-mcp --region us-central1
   ```

### Build Timeout

**Problem**: Cloud Build times out

**Solutions:**
1. Increase build timeout:
   ```bash
   gcloud builds submit --timeout=20m
   ```
2. Use larger machine type in `cloudbuild.yaml`:
   ```yaml
   options:
     machineType: 'N1_HIGHCPU_8'
   ```

---

## Security Best Practices

1. **Enable Cloud Armor** for DDoS protection
2. **Use Secret Manager** for sensitive configuration
3. **Enable VPC Service Controls** for network security
4. **Set up Cloud Monitoring** for alerts
5. **Use Identity-Aware Proxy** for authenticated access
6. **Regularly update dependencies** and base images

---

## Monitoring and Logging

### View Metrics

```bash
# Cloud Run metrics in console
gcloud run services describe malaylanguage-mcp \
  --region us-central1 \
  --format 'value(status.url)'

# Then visit: https://console.cloud.google.com/run
```

### Set Up Alerts

```bash
# Example: Alert on high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

---

## Next Steps

1. ✅ Deploy your service using one of the options above
2. ✅ Get your service URL
3. ✅ Configure your MCP client
4. ✅ Test the connection
5. ✅ Set up monitoring and alerts
6. ✅ (Optional) Configure custom domain
7. ✅ (Optional) Set up CI/CD with Cloud Build triggers

For more information and support:
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Repository Issues](https://github.com/zairulanuar/MalayLanguage/issues)

---

## Additional Resources

- [Cloud Run Pricing Calculator](https://cloud.google.com/products/calculator)
- [Best Practices for Cloud Run](https://cloud.google.com/run/docs/best-practices)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
