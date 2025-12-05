# Prompt Test Agent

> **AI-powered test generation framework that automatically creates comprehensive test suites from any web page using AI models.**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/Playwright-1.56-green.svg)](https://playwright.dev/)
[![Multi-Provider](https://img.shields.io/badge/LLM-Multi--Provider-brightgreen.svg)](LLM_PROVIDER_GUIDE.md)

## 🎯 What Does This Do?

Prompt Test Agent analyzes your web application and **automatically generates comprehensive test specifications** using AI:

### Test Types Generated

| Category | What It Tests | Example |
|----------|---------------|---------|
| ✅ **Functional** | User workflows, form validation, navigation | "User can login with valid credentials" |
| ⚡ **Performance** | Page load times, response times, resource usage | "Page loads within 2 seconds" |
| 🔒 **Security** | Authentication, input validation, OWASP vulnerabilities | "Login form prevents SQL injection" |
| ♿ **Accessibility** | WCAG compliance, keyboard navigation, screen readers | "All buttons have ARIA labels" |
| 🎨 **Usability** | Error messages, form design, user experience | "Error messages are clear and helpful" |
| 🛡️ **Reliability** | Error handling, failover, data integrity | "System recovers from network failures" |

### Key Features

- 🚀 **No manual test writing** - Just provide a URL, get JSON test specifications
- 🔒 **100% Local AI or Cloud** - Choose between local Ollama or cloud providers (OpenAI, Claude, Gemini)
- ⚡ **Fast generation** - Concurrent processing generates both test types in 30-60 seconds
- 📊 **Structured output** - JSON format ready for CI/CD integration
- 🛡️ **Security-first** - Built-in protection against SSRF, path traversal, code injection
- 🔧 **Flexible** - Mix and match models for optimal cost/quality (e.g., GPT-4 for tests, GPT-3.5 for code)

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [LLM Provider Setup](#-llm-provider-setup)
3. [Installation](#-installation)
4. [Usage Guide](#-usage-guide)
5. [Configuration](#-configuration)
6. [Understanding the Output](#-understanding-the-output)
7. [Troubleshooting](#-troubleshooting)
8. [FAQ](#-faq)

---

## 🚀 Quick Start

### Choose Your LLM Provider

**Option 1: Ollama (Free, Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download models
ollama pull llama3.2
ollama pull deepseek-coder:6.7b

# Configure
cat > .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_CODING_MODEL=deepseek-coder:6.7b
OLLAMA_BASE_URL=http://localhost:11434
EOF
```

**Option 2: OpenAI (Best Quality)**
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_CODING_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-key-here
EOF
```

**Option 3: Google Gemini (Free Tier)**
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_CODING_MODEL=gemini-pro
GOOGLE_API_KEY=your-key-here
EOF
```

### Install and Run

```bash
# 1. Clone and install
git clone https://github.com/GanduriKumar/prompt-test-agent.git
cd prompt-test-agent
pip install -r requirements.txt
playwright install chromium

# 2. Generate tests
python cua_agent.py
Enter the URL to open: https://example.com
```

**Output:** `generated_tests.json` with 30-50 test cases in 30-60 seconds

---

## 🤖 LLM Provider Setup

### Quick Comparison

| Provider | Cost | Speed | Quality | Setup Time | Best For |
|----------|------|-------|---------|------------|----------|
| **Ollama** | Free | Medium-Fast | Good | 10 min | Development, Privacy |
| **OpenAI** | $0.01-0.03/1K tokens | Fast | Excellent | 2 min | Production, Best Quality |
| **Google Gemini** | Free tier | Fast | Very Good | 2 min | Budget, High Volume |
| **Anthropic Claude** | $0.003-0.015/1K tokens | Fast | Excellent | 2 min | Complex Reasoning |
| **Azure OpenAI** | Similar to OpenAI | Fast | Excellent | 5 min | Enterprise |

### Ollama (Recommended for Getting Started)

**Pros:** Free, runs locally, no API keys, complete privacy  
**Cons:** Requires 8GB+ RAM, slower on CPU

```bash
# Install
curl -fsSL https://ollama.ai/install.sh | sh  # or download from ollama.ai

# Start server (keep terminal open)
ollama serve

# Download models
ollama pull llama3.2           # Main model (~2GB)
ollama pull deepseek-coder:6.7b # Code model (~4GB)

# Configure .env
cat > .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_CODING_MODEL=deepseek-coder:6.7b
OLLAMA_BASE_URL=http://localhost:11434
EOF
```

### OpenAI (Recommended for Production)

**Pros:** Best quality, fast, reliable  
**Cons:** Costs money, requires API key

```bash
# Get API key: https://platform.openai.com/api-keys

# Configure .env
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_CODING_MODEL=gpt-3.5-turbo     # Use cheaper model for code
OPENAI_API_KEY=sk-your-actual-key
EOF
```

**Cost Example:** ~$0.10-0.30 per test generation (40 tests)

### Google Gemini (Recommended for Cost)

**Pros:** Free tier (60 requests/min), good quality  
**Cons:** Rate limits on free tier

```bash
# Get API key: https://makersuite.google.com/app/apikey

# Configure .env
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_CODING_MODEL=gemini-pro
GOOGLE_API_KEY=your-actual-key
EOF
```

### Anthropic Claude

**Pros:** Excellent reasoning, 200k context  
**Cons:** Similar cost to GPT-4

```bash
# Get API key: https://console.anthropic.com/account/keys

# Configure .env
cat > .env << EOF
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-your-actual-key
EOF
```

### Azure OpenAI (Enterprise)

**Pros:** SLA, compliance, dedicated capacity  
**Cons:** Complex setup, enterprise pricing

```bash
# Setup: https://portal.azure.com

# Configure .env
cat > .env << EOF
LLM_PROVIDER=azure
LLM_MODEL=gpt-4
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_API_VERSION=2024-02-15-preview
EOF
```

**For detailed setup:** See [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md)

---

## 📦 Installation

### Basic Installation (Required for All Providers)

```bash
# Step 1: Clone the repository
git clone https://github.com/GanduriKumar/prompt-test-agent.git
cd prompt-test-agent

# Step 2: Install Python dependencies (includes all provider SDKs)
pip install -r requirements.txt

# Step 3: Install browser for automation
playwright install chromium
```

### LLM Provider Setup (Choose One or More)

#### Option A: Ollama (Local, Free)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start server (in separate terminal)
ollama serve

# Download models
ollama pull llama3.2
ollama pull deepseek-coder:6.7b

# Configure
cat > .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_CODING_MODEL=deepseek-coder:6.7b
OLLAMA_BASE_URL=http://localhost:11434
EOF
```

#### Option B: OpenAI (Cloud, Best Quality)

```bash
# Get API key from https://platform.openai.com/api-keys

# Configure
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_CODING_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-actual-key
EOF
```

#### Option C: Google Gemini (Cloud, Free Tier)

```bash
# Get API key from https://makersuite.google.com/app/apikey

# Configure
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_CODING_MODEL=gemini-pro
GOOGLE_API_KEY=your-actual-key
EOF
```

#### Option D: Other Providers

See [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md) for Anthropic Claude and Azure OpenAI setup.

### Verify Your Setup

```bash
# Test your LLM provider configuration
python test_llm_providers.py

# Should output: ✅ All tests passed!
```

### First Test Generation

```bash
# Run the generator
python cua_agent.py

# When prompted, enter a URL:
Enter the URL to open: https://example.com
```

**What happens:**
1. ✅ Initializes your configured LLM provider (Ollama, OpenAI, etc.)
2. ✅ Opens the URL in a browser
3. 🔍 Extracts all interactive elements (buttons, inputs, links)
4. 🤖 AI generates 15-20 functional test cases
5. 🤖 AI generates 15-25 NFR test cases
6. 💾 Saves everything to `generated_tests.json`

**Time:** Varies by provider:
- Ollama (CPU): 30-60 seconds
- Ollama (GPU): 10-20 seconds
- OpenAI/Claude/Gemini: 10-30 seconds

**Output:** 
```
2025-01-15 10:30:45 - INFO - Initialized LLM provider: openai (model: gpt-4-turbo-preview)
2025-01-15 10:30:45 - INFO - Validated URL: https://example.com
2025-01-15 10:30:46 - INFO - Starting test generation for URL: https://example.com
2025-01-15 10:31:10 - INFO - Generated 18 functional tests
2025-01-15 10:31:10 - INFO - Generated 22 NFR tests
2025-01-15 10:31:10 - INFO - Tests saved to: generated_tests.json
2025-01-15 10:31:10 - INFO - Total tests generated: 40
```

---

## 💡 Usage Guide

### Basic Usage (Interactive Mode)

```bash
python cua_agent.py
```

**The tool will:**
1. Prompt you for a URL
2. Validate the URL format
3. Open browser and analyze the page
4. Generate functional tests (happy path, negative cases, boundaries)
5. Generate NFR tests (performance, security, accessibility, usability, reliability)
6. Save results to `generated_tests.json`

**Example Session:**
```
Enter the URL to open: myapp.com/login
2025-01-15 10:30:45 - INFO - Validated URL: https://myapp.com/login
2025-01-15 10:30:46 - INFO - Starting test generation for URL: https://myapp.com/login
2025-01-15 10:30:47 - DEBUG - Extracting interactive elements
2025-01-15 10:30:49 - DEBUG - Found 12 interactive elements
2025-01-15 10:30:50 - DEBUG - Generating functional tests
2025-01-15 10:31:05 - INFO - Generated 15 functional tests
2025-01-15 10:31:06 - DEBUG - Generating NFR tests
2025-01-15 10:31:25 - INFO - Generated 20 NFR tests
2025-01-15 10:31:25 - INFO - Tests saved to: generated_tests.json
2025-01-15 10:31:25 - INFO - Total tests generated: 35
```

### Programmatic Usage (Python API)

```python
import asyncio
from cua_tools import generate_functional_tests, generate_nfr_tests

async def generate_all_tests(url):
    """Generate both functional and NFR tests for a URL."""

    # Define business context (helps AI understand the page)
    context = "User authentication page for e-commerce application"

    # Generate functional tests
    func_tests = await generate_functional_tests(url, context)
    print(f"Generated {len(func_tests)} functional tests")

    # Generate NFR tests with specific requirements
    nfr_requirements = {
        "performance": {
            "page_load_time": "< 2s",
            "time_to_interactive": "< 3s"
        },
        "security": {
            "https_only": True,
            "csrf_protection": True
        }
    }
    nfr_tests = await generate_nfr_tests(url, context, nfr_requirements)
    print(f"Generated {len(nfr_tests)} NFR tests")

    return {
        "functional_tests": func_tests,
        "nfr_tests": nfr_tests
    }

# Run for single URL
tests = asyncio.run(generate_all_tests("https://myapp.com/login"))

# Or batch process multiple URLs
urls = [
    "https://myapp.com/login",
    "https://myapp.com/register",
    "https://myapp.com/checkout"
]

for url in urls:
    tests = asyncio.run(generate_all_tests(url))
    # Save or process tests as needed
```

### URL Input Formats

| Input | Interpreted As | Notes |
|-------|---------------|-------|
| `example.com` | `https://example.com` | HTTPS added automatically |
| `http://localhost:3000` | `http://localhost:3000` | Respects http:// |
| `192.168.1.1/api` | `https://192.168.1.1/api` | IP addresses supported |
| `example.com:8080/admin` | `https://example.com:8080/admin` | Custom ports work |

**Invalid inputs:**
- `file:///etc/passwd` ❌ (security risk)
- `javascript:alert(1)` ❌ (code injection)
- Empty string ❌ (validation error)

---

## ⚙️ Configuration

### Environment Variables (`.env` file)

All configuration options are available in [.env.example](.env.example). Copy and customize for your provider:

```bash
cp .env.example .env
```

**Ollama (Local):**
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_CODING_MODEL=deepseek-coder:6.7b
OLLAMA_BASE_URL=http://localhost:11434
```

**OpenAI (Cloud):**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_CODING_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-actual-key
```

**Google Gemini (Cloud):**
```env
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_CODING_MODEL=gemini-pro
GOOGLE_API_KEY=your-actual-key
```

**Legacy Ollama Configuration (Backward Compatible):**
```env
# Old variables still work, automatically converted to new format
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
CODING_MODEL=deepseek-coder:6.7b
```

For detailed setup instructions for each provider, see [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md).

### Model Selection Guide

**Ollama (Local):**

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 2GB | Fast | Good | General test generation |
| **mistral** | 4GB | Fast | Good | Simple web apps |
| **deepseek-coder:6.7b** | 4GB | Medium | Excellent | Code generation |

**OpenAI (Cloud):**

| Model | Cost/1K tokens | Speed | Quality | Best For |
|-------|----------------|-------|---------|----------|
| **gpt-4-turbo** | $0.01/$0.03 | Fast | Excellent | Production use |
| **gpt-4** | $0.03/$0.06 | Medium | Excellent | Complex test cases |
| **gpt-3.5-turbo** | $0.0005/$0.0015 | Very Fast | Good | Budget-conscious |

**Google (Cloud):**

| Model | Cost/1K tokens | Speed | Quality | Best For |
|-------|----------------|-------|---------|----------|
| **gemini-pro** | Free tier | Fast | Very Good | High volume |
| **gemini-pro-vision** | Free tier | Fast | Very Good | Screenshot analysis |

---

## 📄 Understanding the Output

### Generated File: `generated_tests.json`

**Structure:**
```json
{
  "functional_tests": [
    {
      "id": "FUNC_001",
      "title": "User can login with valid credentials",
      "preconditions": ["User has registered account", "User is on login page"],
      "steps": [
        "Enter valid email address in email field",
        "Enter valid password in password field",
        "Click 'Sign In' button"
      ],
      "expected_result": "User is redirected to dashboard with welcome message",
      "tags": ["authentication", "login", "happy-path", "critical"]
    }
  ],
  "nfr_tests": [
    {
      "id": "NFR_001",
      "category": "performance",
      "title": "Login page loads within 2 seconds",
      "description": "Measure time from navigation to DOMContentLoaded event",
      "acceptance_criteria": [
        "Page load time < 2000ms for 95th percentile",
        "Time to First Byte (TTFB) < 500ms",
        "No JavaScript errors in console"
      ],
      "tooling_suggestions": ["Playwright", "Lighthouse", "WebPageTest"]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Issue 1: Provider Connection Error

**Symptoms:**
```
Error: Connection refused
Error: Invalid API key
```

**Solutions:**

**Ollama:**
```bash
# Check if Ollama is running
curl http://localhost:11434

# If not running:
ollama serve
```

**OpenAI/Cloud Providers:**
```bash
# Verify API key
python test_llm_providers.py

# Check .env file
cat .env | grep API_KEY
```

### Issue 2: Model Not Found

**Symptoms:**
```
Error: model 'llama3.2' not found
Error: The model 'gpt-5' does not exist
```

**Solutions:**

**Ollama:**
```bash
# List installed models
ollama list

# Install missing model
ollama pull llama3.2
ollama pull deepseek-coder:6.7b
```

**OpenAI:**
```env
# Use only valid OpenAI models:
LLM_MODEL=gpt-4-turbo-preview
LLM_MODEL=gpt-4
LLM_MODEL=gpt-3.5-turbo
```

### Issue 3: API Key Invalid or Expired

**Solutions:**

**OpenAI:**
1. Get new key: https://platform.openai.com/api-keys
2. Update .env: `OPENAI_API_KEY=sk-proj-...`
3. Verify key: `python test_llm_providers.py`

**Google:**
1. Get key: https://makersuite.google.com/app/apikey
2. Update .env: `GOOGLE_API_KEY=...`
3. Enable Generative Language API if needed

### Issue 4: Rate Limit Exceeded

**Symptoms:**
```
Error: Rate limit exceeded
429 Too Many Requests
```

**Solutions:**

| Provider | Free Tier Limits | Solution |
|----------|------------------|----------|
| **OpenAI** | 3 RPM (requests/min) | Upgrade to paid tier or use Ollama |
| **Anthropic** | 5 RPM | Upgrade to paid tier |
| **Google** | 60 RPM | Should be sufficient, wait if hit |
| **Ollama** | No limits | Switch to Ollama for development |

### Issue 3: No Tests Generated

**Cause:** Page has no interactive elements or AI model returned invalid JSON

**Solutions:**
```python
# Check what was extracted
from cua_tools import get_interactive_elements
elements = await get_interactive_elements("https://example.com")
print(f"Found {len(elements)} elements")

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```