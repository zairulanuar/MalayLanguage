# Deploying MalayLanguage MCP Server to Hugging Face Spaces

This guide walks you through deploying the MalayLanguage MCP Server to Hugging Face Spaces using Docker.

## Prerequisites

- A Hugging Face account (sign up at [huggingface.co](https://huggingface.co))
- Git installed on your machine
- Basic familiarity with Git and command line

## Deployment Steps

### Method 1: Direct Upload (Recommended for Beginners)

#### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure your Space:
   - **Name**: `malaylanguage-mcp` (or your preferred name)
   - **License**: MIT
   - **Space SDK**: Select **Docker**
   - **Space hardware**: CPU Basic (free tier) or upgrade for better performance

4. Click "Create Space"

#### Step 2: Prepare Files

You'll need to upload these files to your Space:

**Required files:**
- `README.md` (use `README_HF_SPACES.md` content)
- `Dockerfile` (use `Dockerfile.hf` content)
- `requirements.txt`
- `server.py`
- `http_server.py`
- `server.json`

#### Step 3: Upload Files

1. In your new Space, click "Files" → "Add file" → "Upload files"
2. Upload all required files listed above
3. For the README:
   - Rename `README_HF_SPACES.md` to `README.md` before uploading
   - **Important**: Make sure the YAML frontmatter is at the top:
     ```yaml
     ---
     title: MalayLanguage MCP Server
     emoji: 🇲🇾
     colorFrom: blue
     colorTo: green
     sdk: docker
     app_port: 7860
     ---
     ```

4. For the Dockerfile:
   - Upload `Dockerfile.hf` as `Dockerfile` (rename it)

5. Commit the files

#### Step 4: Wait for Build

- Hugging Face will automatically build your Docker image
- This may take 5-10 minutes
- Watch the build logs in the "Logs" tab
- Once complete, your Space will start running

#### Step 5: Test Your Deployment

```bash
# Replace with your actual Space URL
curl https://YOUR_USERNAME-malaylanguage-mcp.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "malaylanguage-mcp-server",
  "version": "1.0.0"
}
```

### Method 2: Git Push (Recommended for Developers)

#### Step 1: Create a New Space

Same as Method 1, Step 1.

#### Step 2: Clone Your Space Repository

```bash
# Clone the empty Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/malaylanguage-mcp
cd malaylanguage-mcp
```

#### Step 3: Copy Required Files

From your MalayLanguage repository:

```bash
# Copy the HF Spaces README (rename to README.md)
cp /path/to/MalayLanguage/README_HF_SPACES.md README.md

# Copy the HF Spaces Dockerfile (rename to Dockerfile)
cp /path/to/MalayLanguage/Dockerfile.hf Dockerfile

# Copy application files
cp /path/to/MalayLanguage/requirements.txt .
cp /path/to/MalayLanguage/server.py .
cp /path/to/MalayLanguage/http_server.py .
cp /path/to/MalayLanguage/server.json .

# Optional: Copy .gitignore
cp /path/to/MalayLanguage/.gitignore .
```

#### Step 4: Verify YAML Frontmatter

Ensure `README.md` starts with the correct frontmatter:

```markdown
---
title: MalayLanguage MCP Server
emoji: 🇲🇾
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---
```

#### Step 5: Commit and Push

```bash
git add .
git commit -m "Initial deployment of MalayLanguage MCP Server"
git push
```

Hugging Face will automatically build and deploy your Space.

## Configuration

### Environment Variables (Optional)

You can add environment variables in Space Settings:

1. Go to your Space page
2. Click "Settings" → "Variables and secrets"
3. Add variables:
   - `PORT`: `7860` (default for HF Spaces)
   - `HOST`: `0.0.0.0`
   - `MALAYA_CACHE`: `/tmp/.malaya`

### Hardware Upgrades

For better performance, consider upgrading your Space hardware:

- **CPU Basic** (Free): Works but may be slow on first load
- **CPU Upgrade** ($0.03/hour): Faster model loading and processing
- **T4 Small** ($0.60/hour): GPU acceleration (not required for this app)

To upgrade:
1. Go to Space Settings → "Hardware"
2. Select your preferred tier
3. Save changes

## Using Your Deployed Space

### Configure MCP Clients

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

**VS Code / Cursor** (`.vscode/mcp.json`):
```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

### Test the Connection

```bash
# Test health endpoint
curl https://YOUR_USERNAME-malaylanguage-mcp.hf.space/health

# Test service info
curl https://YOUR_USERNAME-malaylanguage-mcp.hf.space/

# Or use the automated test script
python test_connection.py https://YOUR_USERNAME-malaylanguage-mcp.hf.space
```

## Performance Considerations

### First Request Delay

⚠️ **Important**: The first request to each tool will be slow (30-90 seconds) because:
- Malaya models are downloaded on-demand (~500MB+ per model)
- Models are cached in `/tmp/.malaya`
- Subsequent requests will be much faster (2-4 seconds)

### Space Sleep Behavior

**Free tier Spaces:**
- Sleep after 48 hours of inactivity
- First request after sleep will wake the Space (takes ~30-60 seconds)
- Models may need to be re-downloaded after restart

**Upgraded Spaces:**
- Can stay always-on (no sleep)
- Faster cold starts
- Persistent storage options available

### Memory Requirements

- Minimum: 4GB RAM (for model loading)
- Recommended: 8GB RAM (for multiple concurrent requests)
- Each loaded model uses ~500MB-1GB of memory

## Monitoring Your Space

### View Logs

1. Go to your Space page
2. Click "Logs" tab
3. Monitor real-time logs for:
   - Server startup
   - Model loading progress
   - Requests and responses
   - Errors

### Check Resource Usage

1. Go to your Space page
2. Check the resource meter at the top
3. Monitor:
   - CPU usage
   - Memory usage
   - Request count

## Troubleshooting

### Space won't build

**Check Dockerfile:**
- Ensure `Dockerfile` (not `Dockerfile.hf`) exists in root
- Verify all required files are present
- Check build logs for specific errors

**Common issues:**
- Missing files: Ensure all required files are uploaded
- Port mismatch: Dockerfile should use port 7860
- User permissions: Dockerfile must use UID 1000

### Space builds but doesn't run

**Check README frontmatter:**
```yaml
sdk: docker
app_port: 7860
```

**Check logs:**
- Look for Python errors
- Verify dependencies installed correctly
- Check if port 7860 is bound correctly

### Models failing to load

**Memory issues:**
- Upgrade to a higher tier with more RAM
- Models require significant memory (~500MB-1GB each)

**Storage issues:**
- `/tmp` should be writable
- Check disk space in logs

### Connection timeouts

**Space sleeping:**
- Free tier sleeps after 48h inactivity
- First request wakes it up (30-60s delay)
- Consider upgrading for always-on

**Network issues:**
- Verify URL is correct
- Check firewall rules
- Ensure using `/sse` endpoint

## Updating Your Space

### Via Git

```bash
cd malaylanguage-mcp
# Make your changes
git add .
git commit -m "Update: description of changes"
git push
```

Hugging Face will rebuild automatically.

### Via Web Interface

1. Go to your Space
2. Click "Files"
3. Click on the file to edit
4. Make changes
5. Commit changes

## Cost Estimation

### Free Tier
- **Cost**: $0
- **Limits**: 
  - Sleeps after 48h inactivity
  - 2 vCPU, 16GB RAM, 50GB storage
  - Shared resources
- **Good for**: Personal use, testing, demos

### CPU Upgrade
- **Cost**: ~$0.03/hour = ~$22/month
- **Benefits**:
  - Always-on option
  - Better performance
  - Dedicated resources
- **Good for**: Production use, regular traffic

## Private Spaces

To make your Space private:

1. Go to Space Settings
2. Change visibility to "Private"
3. Generate access tokens for authorized users
4. Configure MCP clients with tokens:
   ```json
   {
     "mcpServers": {
       "malaylanguage": {
         "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
         "transport": "sse",
         "headers": {
           "Authorization": "Bearer YOUR_HF_TOKEN"
         }
       }
     }
   }
   ```

## Advanced: Persistent Storage

For persistent model caching across restarts:

1. Upgrade to a persistent Space tier
2. Modify Dockerfile to use persistent volume:
   ```dockerfile
   ENV MALAYA_CACHE=/data/.malaya
   ```
3. Models will persist across restarts

## Best Practices

1. **Start with free tier** - Test before upgrading
2. **Monitor logs** - Watch for errors and performance issues
3. **Set up health checks** - Use monitoring services
4. **Document your Space** - Update README with specific instructions
5. **Use secrets** - Store sensitive config in Space secrets
6. **Version control** - Use Git for all changes
7. **Test before promoting** - Create a staging Space first

## Getting Help

- **Hugging Face Docs**: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- **Community Forum**: [discuss.huggingface.co](https://discuss.huggingface.co)
- **MalayLanguage Issues**: [github.com/zairulanuar/MalayLanguage/issues](https://github.com/zairulanuar/MalayLanguage/issues)

## Example Spaces

Looking for inspiration? Check out these example Spaces:

- Search for "MCP Server" on Hugging Face Spaces
- Browse Docker SDK Spaces for deployment patterns
- Check FastAPI/Starlette examples for ASGI patterns

---

**That's it!** Your MalayLanguage MCP Server is now running on Hugging Face Spaces and accessible to MCP clients worldwide. 🎉
