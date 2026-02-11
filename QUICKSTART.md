# Quick Start Example: Deploy and Use in 5 Minutes

This guide shows you how to get the MalayLanguage MCP server running remotely in just 5 minutes.

## Step 1: Deploy (2 minutes)

### Option A: Hugging Face Spaces (Free & Easy) 🆕

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Name**: `malaylanguage-mcp`
   - **Space SDK**: Docker
   - **Hardware**: CPU Basic (free)
4. Upload files (see [HF_SPACES_DEPLOYMENT.md](HF_SPACES_DEPLOYMENT.md) for details)
5. Wait for build (5-10 minutes)
6. Copy your URL: `https://YOUR_USERNAME-malaylanguage-mcp.hf.space`

**Note**: First request may be slow (30-90s) as models download. Free tier sleeps after 48h.

### Option B: Railway (Fast)

1. Click: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/malaylanguage)
2. Sign in with GitHub
3. Click "Deploy"
4. Wait for deployment to complete
5. Copy your URL: `https://your-app.up.railway.app`

### Option C: Docker Compose (Self-hosted)

```bash
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage
docker-compose up -d
```

Your server is now at: `http://localhost:8000`

## Step 2: Test Connection (1 minute)

```bash
# Test your deployment
python test_connection.py https://your-app.up.railway.app

# OR for local
python test_connection.py http://localhost:8000
```

Expected output:
```
============================================================
MalayLanguage MCP Server Connection Test
============================================================
Testing server at: https://your-app.up.railway.app

🔍 Testing health check at https://your-app.up.railway.app/health...
✅ Health check passed!
   Service: malaylanguage-mcp-server
   Version: 1.0.0
...
🎉 All tests passed! Your server is ready to use.
```

## Step 3: Configure Your Client (1 minute)

### For Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-app.up.railway.app/sse",
      "transport": "sse"
    }
  }
}
```

Restart Claude Desktop.

### For VS Code / Cursor

Create: `.vscode/mcp.json`

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-app.up.railway.app/sse",
      "transport": "sse"
    }
  }
}
```

Reload VS Code.

## Step 4: Use the Tools (1 minute)

### In Claude Desktop

Try these prompts:

**Translate:**
```
Use the translate tool to translate "Good morning, how are you?" from English to Malay
```

**Detect Language:**
```
Use detect_language to identify: "Selamat pagi, apa khabar?"
```

**Normalize Text:**
```
Use normalize_malay to fix: "saya x tau la bro"
```

### Example Results

**Translation:**
```
Translation Result:

Source (English): Good morning, how are you?

Translation (Malay): Selamat pagi, apa khabar anda?
```

**Language Detection:**
```
Language Detection Result:
Language: malay
Confidence: 99.8%

Input text: Selamat pagi, apa khabar?
```

**Normalization:**
```
Text Normalization Result:

Original: saya x tau la bro

Normalized: saya tidak tahu la abang
```

## Complete! 🎉

You now have:
- ✅ A remotely deployed MCP server
- ✅ Verified connection
- ✅ Configured MCP client
- ✅ Working Malay language processing tools

## What's Next?

### Explore More Tools

1. **correct_spelling** - Fix spelling errors
   ```
   Use correct_spelling on: "sya ingin mkan nasi"
   ```

2. **rewrite_style** - Change text style
   ```
   Use rewrite_style to make "Saya nak pergi kedai" more formal
   ```

3. **term_lookup** - Get word information
   ```
   Use term_lookup to learn about "sekolah"
   ```

### Monitor Your Deployment

```bash
# Check health
curl https://your-app.up.railway.app/health

# View server info
curl https://your-app.up.railway.app/
```

### Troubleshooting

**Problem: First request is slow (30+ seconds)**
- This is normal! Models are downloading (~500MB)
- Subsequent requests will be fast (<3 seconds)
- Models are cached permanently

**Problem: Connection refused**
- Verify URL: `curl https://your-app.up.railway.app/health`
- Check deployment logs in Railway/Render
- Ensure you're using `/sse` endpoint

**Problem: Tool not found**
- Make sure MCP client sees the server
- Restart your MCP client
- Check client logs for connection errors

### Get Help

- 📖 Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🧪 Testing: [TESTING.md](TESTING.md)
- 🐛 Issues: https://github.com/zairulanuar/MalayLanguage/issues

## Cost

- **Railway**: Free tier (500 hours/month) - Perfect for personal use
- **Render**: Free tier (750 hours/month) - May sleep after inactivity
- **Fly.io**: Free tier (3 VMs) - Good for always-on service
- **Docker Local**: Free - Full control, requires your own server

## Advanced: Production Setup

For production use:

1. **Set up monitoring:**
   ```bash
   # Add UptimeRobot or similar to monitor /health
   ```

2. **Configure alerts:**
   - Set up email/Slack alerts for downtime

3. **Scale as needed:**
   - Railway: Upgrade to Pro for more resources
   - Add load balancer for high traffic

4. **Backup configuration:**
   - Save your MCP client config
   - Document your deployment URL

---

**That's it!** You're now using the MalayLanguage MCP server without any local installation. 🚀
