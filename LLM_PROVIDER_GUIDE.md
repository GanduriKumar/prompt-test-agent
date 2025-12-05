# Multi-Provider LLM Integration Guide

## Overview

The Prompt Test Agent now supports multiple LLM providers, giving you flexibility to choose between local (Ollama) and hosted cloud services (OpenAI, Anthropic, Google, Azure).

## Supported Providers

| Provider | Type | Models | Setup Difficulty | Cost |
|----------|------|--------|------------------|------|
| **Ollama** | Local | LLaMA, Mistral, CodeLlama | Medium | Free |
| **OpenAI** | Cloud | GPT-4, GPT-3.5 | Easy | $$$ |
| **Anthropic** | Cloud | Claude 3 (Opus, Sonnet, Haiku) | Easy | $$$ |
| **Google** | Cloud | Gemini Pro | Easy | $ (Free tier) |
| **Azure OpenAI** | Cloud | GPT-4, GPT-3.5 (Azure-hosted) | Medium | $$$ |

## Quick Start

### 1. Choose Your Provider

**For Free/Local:**
```bash
# Ollama - Run models locally (requires 8GB+ RAM)
LLM_PROVIDER=ollama
```

**For Best Quality:**
```bash
# OpenAI GPT-4 - Highest quality, higher cost
LLM_PROVIDER=openai
```

**For Balanced:**
```bash
# Google Gemini - Good quality, lower cost, free tier
LLM_PROVIDER=google
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your provider settings
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Provider-Specific Setup

### Ollama (Local)

**Advantages:**
- ✅ Free (no API costs)
- ✅ Privacy (data stays local)
- ✅ No rate limits
- ✅ Works offline

**Requirements:**
- 8GB+ RAM (16GB recommended)
- 10GB+ disk space
- Optional: GPU for faster inference

**Setup:**

1. **Install Ollama:**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from: https://ollama.ai/download
   ```

2. **Start Ollama server:**
   ```bash
   ollama serve
   ```

3. **Download models:**
   ```bash
   # Text generation
   ollama pull llama3.2
   
   # Vision (screenshot analysis)
   ollama pull llama3.2-vision
   
   # Code generation
   ollama pull deepseek-coder:6.7b
   ```

4. **Configure .env:**
   ```env
   LLM_PROVIDER=ollama
   LLM_MODEL=llama3.2
   LLM_VISION_MODEL=llama3.2-vision
   LLM_CODING_MODEL=deepseek-coder:6.7b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

**Alternative Models:**
- **Faster:** `llama3.2:8b`, `mistral`
- **Better quality:** `llama3.1:70b`, `mixtral:8x7b` (requires 32GB+ RAM)
- **Smaller:** `gemma2:2b` (for low-end hardware)

---

### OpenAI (GPT-4)

**Advantages:**
- ✅ Highest quality outputs
- ✅ Fast API responses
- ✅ Excellent code generation
- ✅ Superior vision understanding

**Requirements:**
- OpenAI account with credits
- API key

**Setup:**

1. **Get API key:**
   - Visit https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. **Configure .env:**
   ```env
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4-turbo-preview
   LLM_VISION_MODEL=gpt-4-vision-preview
   LLM_CODING_MODEL=gpt-4-turbo-preview
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Model Options:**
- **Best quality:** `gpt-4-turbo-preview` (128k context)
- **Balanced:** `gpt-4-1106-preview` (good speed/quality)
- **Faster/cheaper:** `gpt-3.5-turbo-1106` (16k context)
- **Vision:** `gpt-4-vision-preview` (required for screenshots)

**Cost Estimate:**
- GPT-4: ~$0.20-$0.50 per test generation
- GPT-3.5: ~$0.02-$0.05 per test generation
- Typical project (50 URLs): $10-$25

---

### Anthropic (Claude)

**Advantages:**
- ✅ Excellent reasoning
- ✅ Long context (200k tokens)
- ✅ Strong code generation
- ✅ Good safety/alignment

**Requirements:**
- Anthropic account
- API key

**Setup:**

1. **Get API key:**
   - Visit https://console.anthropic.com/account/keys
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-`)

2. **Configure .env:**
   ```env
   LLM_PROVIDER=anthropic
   LLM_MODEL=claude-3-opus-20240229
   LLM_VISION_MODEL=claude-3-opus-20240229
   LLM_CODING_MODEL=claude-3-opus-20240229
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

**Model Options:**
- **Best quality:** `claude-3-opus-20240229` (highest capability)
- **Balanced:** `claude-3-sonnet-20240229` (good speed/quality)
- **Fastest:** `claude-3-haiku-20240307` (quick responses)

**Cost Estimate:**
- Opus: ~$0.30-$0.70 per test generation
- Sonnet: ~$0.06-$0.15 per test generation
- Haiku: ~$0.01-$0.03 per test generation

---

### Google (Gemini)

**Advantages:**
- ✅ Free tier available (60 requests/min)
- ✅ Fast responses
- ✅ Good vision capabilities
- ✅ Low cost

**Requirements:**
- Google account
- API key

**Setup:**

1. **Get API key:**
   - Visit https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Configure .env:**
   ```env
   LLM_PROVIDER=google
   LLM_MODEL=gemini-pro
   LLM_VISION_MODEL=gemini-pro-vision
   GOOGLE_API_KEY=your-actual-key-here
   ```

**Model Options:**
- **Text:** `gemini-pro` (text-only)
- **Vision:** `gemini-pro-vision` (multimodal)
- **Ultra:** `gemini-ultra` (coming soon, highest quality)

**Free Tier:**
- 60 requests per minute
- 1,500 requests per day
- Sufficient for most testing needs

**Cost Estimate (Paid):**
- ~$0.02-$0.05 per test generation
- Very cost-effective

---

### Azure OpenAI

**Advantages:**
- ✅ Enterprise security
- ✅ Data residency control
- ✅ Integration with Azure services
- ✅ SLA guarantees

**Requirements:**
- Azure account
- Azure OpenAI resource
- Model deployment

**Setup:**

1. **Create Azure OpenAI resource:**
   - Go to Azure Portal
   - Create "Azure OpenAI" resource
   - Note the endpoint URL and key

2. **Deploy models:**
   - In Azure OpenAI Studio
   - Deploy GPT-4 or GPT-3.5 models
   - Note deployment names

3. **Configure .env:**
   ```env
   LLM_PROVIDER=azure
   LLM_MODEL=gpt-4
   AZURE_OPENAI_API_KEY=your-azure-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

**Cost:**
- Same as OpenAI pricing
- Billed through Azure subscription

---

## Advanced Configuration

### Using Different Models for Different Tasks

You can optimize cost and performance by using different models for different tasks:

```env
LLM_PROVIDER=openai

# Use GPT-4 for complex test generation
LLM_MODEL=gpt-4-turbo-preview

# Use GPT-4V for vision (required)
LLM_VISION_MODEL=gpt-4-vision-preview

# Use GPT-3.5 for simple code generation (cheaper)
LLM_CODING_MODEL=gpt-3.5-turbo-1106
```

### Mixing Providers

While not directly supported, you can modify code to use different providers for different tasks:

```python
from llm_provider import LLMProvider

# Use Ollama for most tasks (free)
ollama = LLMProvider(provider="ollama", model="llama3.2")

# Use GPT-4 for critical vision tasks (best quality)
openai = LLMProvider(provider="openai", model="gpt-4-vision-preview")
```

### Custom Endpoints

For self-hosted or custom endpoints:

```env
# OpenAI-compatible endpoint
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
OPENAI_API_KEY=your-key

# Ollama on remote server
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://your-server:11434
```

---

## Performance Comparison

### Speed (Single URL Test Generation)

| Provider | Model | Time | Quality |
|----------|-------|------|---------|
| Ollama (GPU) | llama3.2 | 10-20s | Good |
| Ollama (CPU) | llama3.2 | 30-60s | Good |
| OpenAI | GPT-4 | 15-30s | Excellent |
| OpenAI | GPT-3.5 | 5-10s | Good |
| Anthropic | Claude 3 Opus | 10-25s | Excellent |
| Anthropic | Claude 3 Haiku | 5-10s | Good |
| Google | Gemini Pro | 8-15s | Good |

### Cost (Per URL)

| Provider | Model | Cost/URL | 100 URLs |
|----------|-------|----------|----------|
| Ollama | Any | $0 | $0 |
| OpenAI | GPT-4 | $0.30 | $30 |
| OpenAI | GPT-3.5 | $0.03 | $3 |
| Anthropic | Claude Opus | $0.50 | $50 |
| Anthropic | Claude Sonnet | $0.10 | $10 |
| Google | Gemini Pro | $0.03 | $3 |

### Quality Comparison

**Test Case Quality (subjective rating):**
- GPT-4: ⭐⭐⭐⭐⭐ (best reasoning, most comprehensive)
- Claude 3 Opus: ⭐⭐⭐⭐⭐ (excellent reasoning, detailed)
- Claude 3 Sonnet: ⭐⭐⭐⭐ (very good, balanced)
- GPT-3.5: ⭐⭐⭐⭐ (good quality, faster)
- Gemini Pro: ⭐⭐⭐⭐ (good quality, consistent)
- Ollama (llama3.2): ⭐⭐⭐ (decent, requires tuning)

---

## Troubleshooting

### Error: "Provider not found"

**Cause:** Invalid provider name in `LLM_PROVIDER`

**Solution:**
```env
# Must be one of: ollama, openai, anthropic, google, azure
LLM_PROVIDER=openai
```

### Error: "API key not found"

**Cause:** Missing API key for cloud provider

**Solution:**
```env
# Add the appropriate API key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Error: "Connection refused" (Ollama)

**Cause:** Ollama server not running

**Solution:**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434
```

### Error: "Model not found" (Ollama)

**Cause:** Model not downloaded

**Solution:**
```bash
# List installed models
ollama list

# Download missing model
ollama pull llama3.2
```

### Error: "Rate limit exceeded"

**Cause:** Too many API requests

**Solution:**
1. Add delays between requests
2. Use batch processing
3. Upgrade API plan
4. Switch to Ollama (no limits)

### Error: "Invalid JSON response"

**Cause:** Model not following JSON format

**Solution:**
1. Use newer models (GPT-4, Claude 3, Gemini)
2. Add explicit JSON instructions in prompts
3. Increase temperature for less strict parsing
4. Use Ollama with JSON format enforcement

---

## Best Practices

### 1. Start Local, Scale to Cloud

```bash
# Development: Use Ollama (free, no limits)
LLM_PROVIDER=ollama

# Production: Use cloud provider for quality
LLM_PROVIDER=openai
```

### 2. Use Appropriate Models

- **Critical tests:** GPT-4, Claude Opus
- **Bulk generation:** GPT-3.5, Gemini, Claude Haiku
- **Prototyping:** Ollama

### 3. Monitor Costs

```python
# Track API usage
import logging
logging.info(f"Generated {test_count} tests, estimated cost: ${cost}")
```

### 4. Cache Results

```python
# Cache generated tests to avoid re-generating
import json
from pathlib import Path

cache_file = Path("test_cache.json")
if cache_file.exists():
    with open(cache_file) as f:
        cached_tests = json.load(f)
```

### 5. Fallback Strategy

```python
# Try cloud provider, fallback to Ollama
try:
    provider = LLMProvider(provider="openai")
except Exception:
    logging.warning("OpenAI failed, using Ollama")
    provider = LLMProvider(provider="ollama")
```

---

## Migration Guide

### From Ollama-Only to Multi-Provider

**Old code (Ollama-only):**
```python
# No changes needed - backward compatible!
# Old env vars still work:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VISION_MODEL=llama3.2-vision
CODING_MODEL=deepseek-coder:6.7b
```

**New code (Multi-provider):**
```env
# New env vars for flexibility:
LLM_PROVIDER=ollama  # or openai, anthropic, google, azure
LLM_MODEL=llama3.2
LLM_VISION_MODEL=llama3.2-vision
LLM_CODING_MODEL=deepseek-coder:6.7b
```

**Switching to OpenAI:**
```env
# Just change these two lines:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key

# Models auto-configure to GPT-4 defaults
# Or specify explicitly:
LLM_MODEL=gpt-4-turbo-preview
```

---

## FAQ

**Q: Can I use multiple providers simultaneously?**

A: Not directly, but you can create multiple `LLMProvider` instances:
```python
ollama = LLMProvider(provider="ollama")
openai = LLMProvider(provider="openai")
```

**Q: Which provider is best for my use case?**

A:
- **Experimentation:** Ollama (free)
- **Best quality:** OpenAI GPT-4 or Claude 3 Opus
- **Cost-effective:** Google Gemini or GPT-3.5
- **Enterprise:** Azure OpenAI
- **Privacy-sensitive:** Ollama (local)

**Q: Can I use my own fine-tuned models?**

A: Yes, with OpenAI or Azure OpenAI:
```env
LLM_PROVIDER=openai
LLM_MODEL=ft:gpt-4-0613:your-org::model-id
```

**Q: How do I reduce costs?**

A:
1. Use Ollama for development
2. Use cheaper models (GPT-3.5, Gemini, Claude Haiku)
3. Cache results
4. Reduce prompt sizes
5. Use different models for different tasks

**Q: What if my provider has downtime?**

A: Implement fallback logic:
```python
providers = ["openai", "anthropic", "google", "ollama"]
for provider in providers:
    try:
        llm = LLMProvider(provider=provider)
        result = llm.generate(prompt)
        break
    except Exception as e:
        logging.warning(f"{provider} failed: {e}")
```

---

## Support

For issues or questions:
1. Check `.env.example` for configuration examples
2. Review error messages carefully
3. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
4. Check provider documentation
5. Open an issue on GitHub

---

## Version History

- **v3.0.0:** Multi-provider support added (Ollama, OpenAI, Anthropic, Google, Azure)
- **v2.0.0:** Ollama-only support
- **v1.0.0:** Initial release
