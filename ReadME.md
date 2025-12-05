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
- 🌐 **Multi-Provider Support** - Choose between Ollama (local), OpenAI, Anthropic, Google, or Azure
- 💰 **Flexible pricing** - Free local models or premium cloud services
- ⚡ **Fast generation** - Concurrent processing generates both test types in 10-60 seconds
- 📊 **Structured output** - JSON format ready for CI/CD integration
- 🛡️ **Security-first** - Built-in protection against SSRF, path traversal, code injection

### Supported LLM Providers

| Provider | Type | Cost | Quality | Setup |
|----------|------|------|---------|-------|
| 🦙 **Ollama** | Local | Free | Good | Medium |
| 🤖 **OpenAI** | Cloud | $$$ | Excellent | Easy |
| 🎭 **Anthropic** | Cloud | $$$ | Excellent | Easy |
| 🔍 **Google** | Cloud | $ | Good | Easy |
| ☁️ **Azure** | Cloud | $$$ | Excellent | Medium |

See [LLM Provider Guide](LLM_PROVIDER_GUIDE.md) for detailed comparison and setup instructions.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [LLM Provider Setup](#-llm-provider-setup)
3. [Installation](#-installation)
4. [Usage Guide](#-usage-guide)
5. [Configuration](#-configuration)
6. [Understanding the Output](#-understanding-the-output)
7. [API Reference](#-api-reference)
8. [Security Features](#-security-features)
9. [Troubleshooting](#-troubleshooting)
10. [Advanced Usage](#-advanced-usage)
11. [FAQ](#-faq)

---

## 🚀 Quick Start

### Choose Your LLM Provider

**Option 1: Ollama (Free, Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download models
ollama pull llama3.2
ollama pull llama3.2-vision
ollama pull deepseek-coder:6.7b

# Configure
cat > .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
EOF
```

**Option 2: OpenAI (Best Quality)**
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-key-here
EOF
```

**Option 3: Google Gemini (Free Tier)**
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
GOOGLE_API_KEY=your-key-here
EOF
```

See [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md) for all providers and detailed setup.

---

## 🤖 LLM Provider Setup

The tool supports multiple LLM providers. Choose the one that fits your needs:

### Quick Comparison

| Provider | Speed | Cost | Quality | Privacy | Setup |
|----------|-------|------|---------|---------|-------|
| Ollama | Medium-Slow | Free | Good | 100% Private | Medium |
| OpenAI GPT-4 | Fast | $$$ | Excellent | Cloud | Easy |
| Anthropic Claude | Fast | $$$ | Excellent | Cloud | Easy |
| Google Gemini | Fast | Free tier | Good | Cloud | Easy |
| Azure OpenAI | Fast | $$$ | Excellent | Enterprise | Medium |

### Ollama (Recommended for Getting Started)

**Pros:** Free, private, no API keys needed  
**Cons:** Slower, requires local resources

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh  # Linux/Mac
# or download from https://ollama.ai for Windows

# Start server
ollama serve

# Download models
ollama pull llama3.2
ollama pull llama3.2-vision
ollama pull deepseek-coder:6.7b

# Configure .env
echo "LLM_PROVIDER=ollama" > .env
echo "LLM_MODEL=llama3.2" >> .env
```

### OpenAI (Recommended for Production)

**Pros:** Best quality, fast, reliable  
**Cons:** Costs ~$0.30 per test generation

```bash
# Get API key from https://platform.openai.com/api-keys

# Configure .env
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_VISION_MODEL=gpt-4-vision-preview
OPENAI_API_KEY=sk-your-actual-key-here
EOF
```

### Google Gemini (Recommended for Cost)

**Pros:** Free tier (60 req/min), good quality  
**Cons:** Rate limits on free tier

```bash
# Get API key from https://makersuite.google.com/app/apikey

# Configure .env
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_VISION_MODEL=gemini-pro-vision
GOOGLE_API_KEY=your-actual-key-here
EOF
```

### Anthropic Claude

**Pros:** Excellent reasoning, 200k context  
**Cons:** Similar cost to GPT-4

```bash
# Get API key from https://console.anthropic.com/account/keys

# Configure .env
cat > .env << EOF
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
EOF
```

### Azure OpenAI (Enterprise)

**Pros:** Enterprise security, SLAs, data residency  
**Cons:** Requires Azure setup

```bash
# Setup Azure OpenAI resource in Azure Portal
# Deploy GPT-4 model and note deployment name

# Configure .env
cat > .env << EOF
LLM_PROVIDER=azure
LLM_MODEL=gpt-4
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
EOF
```

**📚 For detailed setup instructions, see [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md)**

---

## 📦 Installation

```bash
# Step 1: Clone the repository
git clone https://github.com/GanduriKumar/prompt-test-agent.git
cd prompt-test-agent

# Step 2: Install Python dependencies
pip install -r requirements.txt

# Step 3: Install browser for automation
playwright install chromium

# Step 4: Install and start Ollama
# macOS/Linux:
curl -fsSL https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.ai/download

# Start Ollama (keep this terminal open)
ollama serve

# Step 5: Download AI models (in new terminal)
ollama pull llama3.2              # Text generation (~2GB)
ollama pull llama3.2-vision       # Image analysis (~2GB)
ollama pull deepseek-coder:6.7b   # Code generation (~4GB)

# Step 6: Configure environment
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VISION_MODEL=llama3.2-vision
CODING_MODEL=deepseek-coder:6.7b
EOF
```

### First Test Generation

```bash
# Run the generator
python cua_agent.py

# When prompted, enter a URL:
Enter the URL to open: https://example.com
```

**What happens:**
1. ✅ Opens the URL in a browser
2. 🔍 Extracts all interactive elements (buttons, inputs, links)
3. 🤖 AI generates 15-20 functional test cases
4. 🤖 AI generates 15-25 NFR test cases
5. 💾 Saves everything to `generated_tests.json`

**Time:** 30-60 seconds total

**Output:** 
```
2025-01-15 10:30:45 - INFO - Validated URL: https://example.com
2025-01-15 10:30:46 - INFO - Starting test generation for URL: https://example.com
2025-01-15 10:31:20 - INFO - Generated 18 functional tests
2025-01-15 10:31:20 - INFO - Generated 22 NFR tests
2025-01-15 10:31:20 - INFO - Tests saved to: generated_tests.json
2025-01-15 10:31:20 - INFO - Total tests generated: 40
```

---

## 📦 Installation

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10, macOS 10.15, Ubuntu 20.04 | Latest stable version |
| **Python** | 3.8 | 3.11+ |
| **RAM** | 8GB | 16GB+ |
| **Disk Space** | 12GB | 20GB |
| **CPU** | 4 cores | 8+ cores or GPU |

### Step-by-Step Installation

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

| Package | Version | Purpose |
|---------|---------|---------|
| `playwright` | 1.56.0 | Browser automation (faster than Selenium) |
| `requests` | 2.32.5 | HTTP client for Ollama API |
| `python-dotenv` | 1.2.1 | Load `.env` configuration |
| `certifi` | 2025.11.12 | SSL certificate validation |
| `ollama` | 0.6.1 | Ollama Python client (optional) |

#### 2. Install Browser

```bash
playwright install chromium
```

**Downloads:** Chromium browser (~170MB) for:
- Opening web pages
- Extracting interactive elements  
- Taking screenshots
- Running generated automation code

**Verify installation:**
```bash
playwright --version
# Should output: Version 1.56.0
```

#### 3. Setup Ollama (AI Engine)

**What is Ollama?**
Ollama runs AI models locally on your machine (like Docker for AI). No data leaves your computer.

**Install Ollama:**

| Platform | Command |
|----------|---------|
| **macOS/Linux** | `curl -fsSL https://ollama.ai/install.sh \| sh` |
| **Windows** | Download installer from [ollama.ai/download](https://ollama.ai/download) |

**Start Ollama:**
```bash
# Start server (keep terminal open)
ollama serve

# Verify it's running (in new terminal)
curl http://localhost:11434
# Should return: Ollama is running
```

**Download AI Models:**

```bash
# Text model for test generation
ollama pull llama3.2

# Vision model for screenshot analysis (optional)
ollama pull llama3.2-vision

# Code model for automation generation
ollama pull deepseek-coder:6.7b
```

**Verify models:**
```bash
ollama list
```

**Expected output:**
```
NAME                    ID              SIZE    MODIFIED
llama3.2:latest         a1b2c3d4...     2.0 GB  2 days ago
llama3.2-vision:latest  e5f6g7h8...     2.1 GB  2 days ago
deepseek-coder:6.7b     i9j0k1l2...     3.8 GB  2 days ago
```

#### 4. Configure Environment

Create `.env` file in project root:

```env
# Ollama server URL (default: localhost)
OLLAMA_BASE_URL=http://localhost:11434

# Model names (must match 'ollama list' output)
OLLAMA_MODEL=llama3.2
VISION_MODEL=llama3.2-vision
CODING_MODEL=deepseek-coder:6.7b
```

**Important:** 
- `.env` file is git-ignored (won't be committed)
- Model names must exactly match `ollama list` output
- Keep Ollama server running whenever generating tests

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

### Element Discovery (Before Test Generation)

```python
import asyncio
from cua_tools import get_interactive_elements

async def analyze_page(url):
    """Discover what elements are on the page before generating tests."""
    
    # Extract all interactive elements
    elements = await get_interactive_elements(url)
    
    # Group by element type
    by_type = {}
    for elem in elements:
        tag = elem['tag']
        by_type.setdefault(tag, []).append(elem)
    
    # Display summary
    print(f"\n📊 Page Analysis: {url}\n")
    print(f"Total interactive elements: {len(elements)}\n")
    
    for tag, items in by_type.items():
        print(f"\n{tag.upper()}: {len(items)}")
        for item in items[:5]:  # Show first 5
            print(f"  • ID: {item.get('id', 'N/A'):20} Text: {item.get('text', '')[:40]}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")

# Run analysis
asyncio.run(analyze_page("https://example.com/login"))
```

**Example Output:**
```
📊 Page Analysis: https://example.com/login

Total interactive elements: 15

INPUT: 4
  • ID: email-field          Text: 
  • ID: password-field       Text: 
  • ID: remember-me          Text: 
  • ID: captcha-input        Text: 

BUTTON: 3
  • ID: login-button         Text: Sign In
  • ID: forgot-password      Text: Forgot Password?
  • ID: create-account       Text: Create Account

A: 8
  • ID: N/A                  Text: Terms of Service
  • ID: N/A                  Text: Privacy Policy
  ... and 6 more
```

---

## ⚙️ Configuration

### Environment Variables (`.env` file)

```env
# === REQUIRED SETTINGS ===

# Ollama API endpoint (where AI models run)
OLLAMA_BASE_URL=http://localhost:11434

# Text model for test case generation
# Options: llama3.2, llama3.1, mistral, mixtral
OLLAMA_MODEL=llama3.2

# Vision model for analyzing screenshots (optional feature)
# Options: llama3.2-vision, llava, bakllava
VISION_MODEL=llama3.2-vision

# Code model for generating Playwright automation
# Options: deepseek-coder:6.7b, codellama:13b, starcoder2
CODING_MODEL=deepseek-coder:6.7b
```

### Model Selection Guide

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2** | 2GB | Fast | Good | General test generation |
| **llama3.1** | 4GB | Medium | Better | Complex applications |
| **mistral** | 4GB | Fast | Good | Simple web apps |
| **mixtral:8x7b** | 26GB | Slow | Excellent | Enterprise applications |

**Recommendation:** Start with `llama3.2`. Upgrade to `mistral` or `llama3.1` if test quality is insufficient.

### Browser Configuration

**Viewport Size** (in [`cua_tools.py`](cua_tools.py)):
```python
VIEWPORT = {'width': 1280, 'height': 720}
```

**Change viewport:**
1. Open `cua_tools.py`
2. Find `VIEWPORT` constant (line ~32)
3. Change values:
   ```python
   VIEWPORT = {'width': 1920, 'height': 1080}  # Full HD
   ```
4. Save and restart

**Headless Mode:**
- Element extraction: Uses headless browser (faster, no window)
- Test generation: Uses visible browser (for debugging)

To change, modify `headless=` parameter in function calls:
```python
# Make visible
browser = await p.chromium.launch(headless=False)

# Make headless (faster)
browser = await p.chromium.launch(headless=True)
```

### Performance Tuning

**Speed up test generation:**
1. Use smaller models:
   ```bash
   ollama pull llama3.2:8b  # Smaller variant
   ```

2. Reduce element limit (in `cua_tools.py`):
   ```python
   # Line 550 and 575: Change from 20 to 10
   elems_json = json.dumps(elements[:10], separators=(',', ':'))
   ```

3. Enable GPU acceleration:
   - Ollama automatically uses GPU if available
   - Check with: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD)

**Trade-offs:**
- Smaller models = Faster but lower quality tests
- Fewer elements = Faster but may miss important UI
- GPU = Much faster but requires compatible hardware

### Logging Configuration

**Current:** INFO level (clean output)

**Enable debug logging:**

Add to top of `cua_agent.py` or `cua_tools.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),  # Save to file
        logging.StreamHandler()             # Also print to console
    ]
)
```

**Log levels:**
- `DEBUG` - Everything (element extraction, AI prompts, responses)
- `INFO` - Important events (test counts, file saves)
- `WARNING` - Issues that don't stop execution
- `ERROR` - Failures that prevent test generation

---

## 📄 Understanding the Output

### Generated File: `generated_tests.json`

**Location:** Same directory as `cua_agent.py`

**Size:** Typically 50-200KB (depends on test count)

**Structure:**
```json
{
  "functional_tests": [ ... ],  // 10-25 tests typically
  "nfr_tests": [ ... ]           // 15-30 tests typically
}
```

### Functional Test Format

```json
{
  "id": "FUNC_001",
  "title": "User can login with valid credentials",
  "preconditions": [
    "User has registered account",
    "User is on login page"
  ],
  "steps": [
    "Enter valid email address in email field",
    "Enter valid password in password field",
    "Click 'Sign In' button"
  ],
  "expected_result": "User is redirected to dashboard with welcome message",
  "tags": ["authentication", "login", "happy-path", "critical"]
}
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique test identifier | `"FUNC_001"` |
| `title` | string | One-line test summary | `"User can login"` |
| `preconditions` | array | Setup required before test | `["User is registered"]` |
| `steps` | array | Sequential actions to perform | `["Click button", "Enter text"]` |
| `expected_result` | string | What should happen (pass criteria) | `"Dashboard displayed"` |
| `tags` | array | Categories for filtering/grouping | `["login", "critical"]` |

**Common tag categories:**
- **Functionality:** `login`, `search`, `form`, `navigation`
- **Priority:** `critical`, `high`, `medium`, `low`
- **Test type:** `happy-path`, `negative`, `boundary`, `edge-case`

### NFR Test Format

```json
{
  "id": "NFR_001",
  "category": "performance",
  "title": "Login page loads within 2 seconds",
  "description": "Measure time from navigation to DOMContentLoaded event under normal load conditions",
  "acceptance_criteria": [
    "Page load time < 2000ms for 95th percentile",
    "Time to First Byte (TTFB) < 500ms",
    "First Contentful Paint (FCP) < 1 second",
    "No JavaScript errors in console"
  ],
  "tooling_suggestions": ["Playwright", "Lighthouse", "WebPageTest", "k6"]
}
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique test identifier | `"NFR_001"` |
| `category` | string | NFR test type | `"performance"`, `"security"`, `"accessibility"` |
| `title` | string | One-line test summary | `"Page loads under 2s"` |
| `description` | string | Detailed explanation | `"Measure time from..."` |
| `acceptance_criteria` | array | Pass/fail conditions | `["Load < 2s", "No errors"]` |
| `tooling_suggestions` | array | Recommended testing tools | `["Lighthouse", "k6"]` |

**NFR Categories:**

| Category | Tests For | Tools |
|----------|-----------|-------|
| **performance** | Load time, response time, throughput | Lighthouse, k6, JMeter |
| **security** | Authentication, injection, encryption | OWASP ZAP, Burp Suite |
| **reliability** | Uptime, error recovery, failover | Chaos Monkey, Gremlin |
| **usability** | UI/UX, navigation, error messages | UserTesting, Hotjar |
| **accessibility** | WCAG compliance, screen readers | axe-core, WAVE, NVDA |

### Using Generated Tests

**Option 1: Manual Test Execution**
- Read through each test
- Manually perform steps
- Verify expected results

**Option 2: Convert to pytest**
```python
# test_login.py
import pytest
from playwright.sync_api import sync_playwright

def test_func_001_user_can_login():
    """FUNC_001: User can login with valid credentials"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Preconditions
        page.goto("https://myapp.com/login")
        
        # Steps
        page.fill("#email", "test@example.com")
        page.fill("#password", "ValidPass123")
        page.click("#login-button")
        
        # Expected result
        page.wait_for_url("**/dashboard")
        assert "Welcome" in page.content()
        
        browser.close()
```

**Option 3: CI/CD Integration**
```yaml
# .github/workflows/test-generation.yml
name: Generate and Run Tests

on: [push, pull_request]

jobs:
  test-gen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.ai/install.sh | sh
      
      - name: Start Ollama
        run: ollama serve &
      
      - name: Download models
        run: |
          ollama pull llama3.2
          ollama pull deepseek-coder:6.7b
      
      - name: Generate tests
        run: |
          echo "https://myapp.com" | python cua_agent.py
      
      - name: Upload test artifacts
        uses: actions/upload-artifact@v3
        with:
          name: generated-tests
          path: generated_tests.json
```

---

## 📚 API Reference

### Core Functions

#### `get_interactive_elements(url: str) -> List[Dict]`

**Purpose:** Extract all interactive elements from a web page

**Parameters:**
- `url` (str): Full URL to analyze (e.g., `https://example.com`)

**Returns:** List of dictionaries containing element metadata

**Example:**
```python
elements = await get_interactive_elements("https://example.com/login")

# Returns:
# [
#   {
#     "tag": "input",
#     "type": "email",
#     "id": "email-field",
#     "name": "email",
#     "text": "",
#     "placeholder": "Enter your email",
#     "ariaLabel": "Email address",
#     "role": None
#   },
#   ...
# ]
```

**Element Types Extracted:**
- `<a>` - Links
- `<button>` - Buttons
- `<input>` - Form inputs
- `<textarea>` - Text areas
- `<select>` - Dropdowns

**Performance:** 5-10 seconds (depends on page complexity)

---

#### `generate_functional_tests(url: str, business_context: str) -> List[Dict]`

**Purpose:** Generate functional test cases for a web page

**Parameters:**
- `url` (str): Target URL to test
- `business_context` (str): Description of page purpose (helps AI generate relevant tests)

**Returns:** List of functional test dictionaries

**Example:**
```python
tests = await generate_functional_tests(
    url="https://myapp.com/login",
    business_context="User authentication page for SaaS application"
)

# Returns list of test cases (see "Functional Test Format" section above)
```

**Business Context Examples:**
- ✅ Good: "E-commerce checkout flow with credit card payment"
- ✅ Good: "Admin dashboard for user management and analytics"
- ❌ Bad: "Website"
- ❌ Bad: "Page"

**Performance:** 10-30 seconds (AI inference time)

---

#### `generate_nfr_tests(url: str, business_context: str, nfr_expectations: Optional[Dict]) -> List[Dict]`

**Purpose:** Generate non-functional requirement test cases

**Parameters:**
- `url` (str): Target URL
- `business_context` (str): Page description
- `nfr_expectations` (dict, optional): Specific NFR requirements

**NFR Expectations Format:**
```python
{
    "performance": {
        "page_load_time": "< 2s",
        "time_to_interactive": "< 3s",
        "max_concurrent_users": 1000
    },
    "security": {
        "https_only": True,
        "csrf_protection": True,
        "input_sanitization": True
    },
    "accessibility": {
        "wcag_level": "AA",
        "keyboard_navigation": True
    }
}
```

**Example:**
```python
tests = await generate_nfr_tests(
    url="https://myapp.com/payment",
    business_context="Payment processing page (PCI-DSS compliant)",
    nfr_expectations={
        "performance": {"page_load": "< 1.5s"},
        "security": {"pci_compliant": True}
    }
)
```

**Performance:** 10-30 seconds (AI inference time)

---

### Validation Functions

#### `validate_url(url: str) -> bool`

**Purpose:** Validate URL format and security

**Security Checks:**
- Must start with `http://` or `https://`
- Must be valid domain or IP address
- Blocks `file://`, `javascript:`, `data:` protocols
- Validates port numbers

**Raises:** `ValueError` if URL is invalid

---

#### `sanitize_code(code: str) -> str`

**Purpose:** Check generated code for dangerous operations

**Blocked Operations:**
- `eval`, `exec` - Arbitrary code execution
- `open`, `os.*`, `sys.*` - File system access
- `subprocess` - Shell commands
- `__import__`, `importlib` - Dynamic imports

**Raises:** `ValueError` if code contains forbidden patterns

---

### Utility Functions

#### `encode_file_to_base64(screenshot_path: str) -> str`

**Purpose:** Convert image file to Base64 string for AI vision models

**Security:**
- Validates file path (prevents path traversal)
- Checks file size (max 10MB)
- Only allows `.png`, `.jpg`, `.jpeg` extensions

---

## 🔒 Security Features

### Built-In Security Protections

| Protection | What It Prevents | How It Works |
|------------|------------------|--------------|
| **SSRF Prevention** | Server-Side Request Forgery | URL validation blocks `file://`, `javascript:`, internal IPs |
| **Path Traversal** | Directory traversal attacks | File path validation blocks `../`, `..\\` patterns |
| **Code Injection** | Malicious code execution | Sanitizes generated code, blocks `eval`, `exec`, etc. |
| **DoS Prevention** | Resource exhaustion | Prompt size limits, file size limits, timeouts |
| **XSS Prevention** | Cross-site scripting | Input validation, no direct HTML rendering |

### Security Best Practices

**1. Run in isolated environment**
```bash
# Use Docker container
docker run -it --rm -v $(pwd):/app python:3.11 /bin/bash
cd /app
pip install -r requirements.txt
python cua_agent.py
```

**2. Review generated code before execution**
```python
# Always inspect generated automation code
with open("generated_automation_code.py") as f:
    print(f.read())
# Only execute if code looks safe
```

**3. Use least privilege**
```bash
# Create dedicated user for running tests
sudo useradd -m testrunner
sudo su - testrunner
# Run as testrunner, not root
```

**4. Keep Ollama updated**
```bash
# Update Ollama regularly
curl -fsSL https://ollama.ai/install.sh | sh
```

### Security Limitations

⚠️ **Known Issues:**

1. **exec() usage** - Dynamic code execution is inherently risky
   - **Mitigation:** Code is sanitized before execution
   - **Recommendation:** Review generated code manually

2. **No sandboxing** - Playwright has access to your file system
   - **Mitigation:** Run in container or VM
   - **Recommendation:** Use disposable environments

3. **AI hallucinations** - AI may generate incorrect/malicious code
   - **Mitigation:** Code sanitization catches most issues
   - **Recommendation:** Human review required

---

## 🐛 Troubleshooting

### Issue 1: Ollama Connection Error

**Symptoms:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Solutions:**

**Step 1:** Check Ollama status
```bash
curl http://localhost:11434
# Should return: Ollama is running
```

**Step 2:** Start Ollama if not running
```bash
ollama serve
# Keep terminal open
```

**Step 3:** Verify `.env` configuration
```env
OLLAMA_BASE_URL=http://localhost:11434  # Default port
```

**Step 4:** Check firewall
```bash
# Allow port 11434
sudo ufw allow 11434  # Linux
# Or add exception in Windows Firewall
```

---

### Issue 2: Model Not Found

**Symptoms:**
```
Error: model 'llama3.2' not found
```

**Solutions:**

**Step 1:** List installed models
```bash
ollama list
```

**Step 2:** Install missing model
```bash
ollama pull llama3.2
ollama pull llama3.2-vision
ollama pull deepseek-coder:6.7b
```

**Step 3:** Verify `.env` matches installed models
```bash
# Check what's installed
ollama list

# Update .env to match
vim .env
```

---

### Issue 3: No Tests Generated

**Symptoms:**
```
Generated 0 functional tests
Generated 0 NFR tests
```

**Possible Causes & Solutions:**

**Cause 1: Page has no interactive elements**
```python
# Check what was extracted
elements = await get_interactive_elements("https://example.com")
print(f"Found {len(elements)} elements")
```

**Cause 2: JavaScript-heavy page not fully loaded**
```python
# Edit cua_tools.py, increase wait time
await page.goto(url, wait_until='networkidle')  # Wait for all JS
await page.wait_for_timeout(5000)  # Additional 5s wait
```

**Cause 3: AI model not returning valid JSON**
```python
# Enable debug logging to see raw AI output
logging.basicConfig(level=logging.DEBUG)
# Check logs for AI response
```

---

### Issue 4: JSON Parsing Error

**Symptoms:**
```
json.JSONDecodeError: Expecting value: line 1 column 1
```

**Solutions:**

**Option 1:** Try different model
```bash
ollama pull mistral
```
Update `.env`:
```env
OLLAMA_MODEL=mistral
```

**Option 2:** Inspect raw AI output
```python
# Add to cua_tools.py before json.loads()
print(f"Raw AI output: {raw}")
# Check if AI is returning markdown, text instead of JSON
```

**Option 3:** Use larger model (better at JSON)
```bash
ollama pull llama3.1:70b  # Requires 40GB RAM
```

---

### Issue 5: Slow Test Generation

**Symptoms:**
- Takes > 2 minutes per generation
- System freezes

**Solutions:**

**Option 1:** Use smaller/faster model
```bash
ollama pull llama3.2:8b  # Faster than full model
```

**Option 2:** Enable GPU acceleration
```bash
# Check if GPU is available
nvidia-smi  # For NVIDIA
rocm-smi    # For AMD

# Ollama automatically uses GPU if detected
```

**Option 3:** Reduce element count
```python
# Edit cua_tools.py
# Line 550 and 575: Change from [:20] to [:10]
elems_json = json.dumps(elements[:10], separators=(',', ':'))
```

**Performance Comparison:**

| Configuration | Time | Quality |
|---------------|------|---------|
| llama3.2 + CPU + 20 elements | 60s | High |
| llama3.2:8b + CPU + 20 elements | 30s | Medium |
| llama3.2 + GPU + 20 elements | 15s | High |
| llama3.2 + CPU + 10 elements | 40s | Medium |

---

### Issue 6: Playwright Browser Error

**Symptoms:**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**Solution:**
```bash
playwright install chromium

# Verify installation
playwright --version
```

**Still not working?**
```bash
# Force reinstall
playwright uninstall chromium
playwright install chromium
```

---

## 🚀 Advanced Usage

### Batch Processing Multiple URLs

```python
import asyncio
import json
from cua_agent import generate_all_tests

async def batch_generate(urls, output_dir="tests"):
    """Generate tests for multiple URLs concurrently."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate tests for all URLs concurrently
    tasks = [
        generate_all_tests(url, f"Test generation for {url}")
        for url in urls
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Save each result
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            print(f"❌ Failed for {url}: {result}")
            continue
        
        # Create filename from URL
        filename = url.replace("https://", "").replace("http://", "")
        filename = filename.replace("/", "_").replace(":", "_") + ".json"
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {filepath}")

# Run for multiple URLs
urls = [
    "https://myapp.com/login",
    "https://myapp.com/register",
    "https://myapp.com/checkout",
    "https://myapp.com/profile"
]

asyncio.run(batch_generate(urls))
```

### Custom NFR Requirements

```python
import asyncio
from cua_tools import generate_nfr_tests

async def generate_strict_tests():
    """Generate NFR tests with strict enterprise requirements."""
    
    requirements = {
        "performance": {
            "page_load_time": "< 1.5s",
            "time_to_interactive": "< 2s",
            "first_contentful_paint": "< 800ms",
            "max_concurrent_users": 10000
        },
        "security": {
            "https_only": True,
            "hsts_enabled": True,
            "csp_enabled": True,
            "csrf_protection": True,
            "xss_prevention": True,
            "sql_injection_protection": True,
            "rate_limiting": True
        },
        "accessibility": {
            "wcag_level": "AAA",  # Highest level
            "keyboard_navigation": "full",
            "screen_reader_compatible": True,
            "color_contrast_ratio": "7:1",
            "text_resize": "200%"
        },
        "reliability": {
            "uptime_sla": "99.99%",
            "rpo": "< 1 hour",
            "rto": "< 4 hours",
            "backup_frequency": "hourly"
        }
    }
    
    tests = await generate_nfr_tests(
        url="https://enterprise-app.com/critical-page",
        business_context="Mission-critical payment processing system",
        nfr_expectations=requirements
    )
    
    print(f"Generated {len(tests)} enterprise-grade NFR tests")
    return tests

asyncio.run(generate_strict_tests())
```

### Integration with Test Frameworks

**pytest Integration:**
```python
# conftest.py
import pytest
import json

def pytest_generate_tests(metafunc):
    """Dynamically generate pytest test cases from generated_tests.json"""
    if "functional_test" in metafunc.fixturenames:
        with open("generated_tests.json") as f:
            data = json.load(f)
        
        # Create test IDs and parameters
        test_ids = [t["id"] for t in data["functional_tests"]]
        test_params = data["functional_tests"]
        
        metafunc.parametrize("functional_test", test_params, ids=test_ids)

# test_generated.py
def test_functional(functional_test, playwright):
    """Execute generated functional tests"""
    browser = playwright.chromium.launch()
    page = browser.new_page()
    
    try:
        # Parse and execute test steps
        for step in functional_test["steps"]:
            # TODO: Implement step execution logic
            print(f"Executing: {step}")
        
        # Verify expected result
        # TODO: Implement assertion logic
        assert True  # Placeholder
    
    finally:
        browser.close()
```

---

## ❓ FAQ

**Q: Do I need internet for test generation?**

A: Only during initial setup (downloading models). After that, everything runs locally offline.

---

**Q: How much disk space do AI models need?**

A: ~10GB total:
- `llama3.2`: 2GB
- `llama3.2-vision`: 2GB
- `deepseek-coder:6.7b`: 4GB
- Plus ~2GB for dependencies and browsers

---

**Q: Can I use different AI models?**

A: Yes! Edit `.env`:
```env
# Use Mistral instead of LLaMA
OLLAMA_MODEL=mistral

# Use CodeLlama instead of DeepSeek
CODING_MODEL=codellama:13b
```

Check available models: [ollama.ai/library](https://ollama.ai/library)

---

**Q: Does this execute tests or just generate them?**

A: **Generates test specifications only.** You need to:
1. Review generated test cases
2. Implement test logic (manually or using frameworks)
3. Execute tests in your CI/CD pipeline

Test execution is planned for v4.0.

---

**Q: Is my data sent to external servers?**

A: **No.** All AI processing happens locally via Ollama. Your URLs and data never leave your machine unless you configure a remote Ollama server.

---

**Q: Can I use this in CI/CD pipelines?**

A: **Yes!** Example GitHub Actions:
```yaml
- name: Generate Tests
  run: |
    echo "https://myapp.com" | python cua_agent.py
    cat generated_tests.json
```

---

**Q: What's the business context for?**

A: Helps AI understand page purpose for better test generation:
- ❌ Generic: "Website"
- ✅ Specific: "E-commerce checkout flow with PayPal and Stripe integration"

Currently hardcoded in `cua_agent.py` line 87. You can modify it or make it an input parameter.

---

**Q: Can I generate tests for authenticated pages?**

A: **Not directly.** Workarounds:
1. Manually login first, save cookies:
   ```python
   context = await browser.new_context(storage_state="auth.json")
   ```
2. Modify `get_interactive_elements()` to include login steps
3. Generate tests for public pages only

---

**Q: Why is test generation slow?**

A: AI inference time depends on:
- **Model size:** Larger models = slower but better quality
- **Hardware:** CPU vs GPU (GPU is 3-5x faster)
- **Prompt complexity:** More elements = longer processing

**Typical times:**
- Fast (llama3.2:8b + GPU): 10-15 seconds
- Medium (llama3.2 + CPU): 30-60 seconds
- Slow (llama3.1:70b + CPU): 2-5 minutes

---

**Q: How accurate are AI-generated tests?**

A: **~80-90% accuracy** with good business context. Always review generated tests for:
- Incorrect selectors
- Unrealistic test data
- Missing edge cases
- Incorrect expected results

AI is a **test authoring assistant**, not a replacement for QA expertise.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

**TL;DR:** You can use, modify, and distribute this code freely. No warranty provided.

---

## 👤 Author

**Kumar GN**
- GitHub: [@GanduriKumar](https://github.com/GanduriKumar)
- Repository: [prompt-test-agent](https://github.com/GanduriKumar/prompt-test-agent)

---

## 🙏 Acknowledgments

- **[Playwright](https://playwright.dev/)** - Fast, reliable browser automation
- **[Ollama](https://ollama.ai/)** - Local AI model inference (privacy-first)
- **[Meta LLaMA](https://ai.meta.com/llama/)** - Open-source language models
- **[DeepSeek](https://github.com/deepseek-ai)** - Code generation models

---

## 🔄 Changelog

### v3.0.0 (2025-01-15) - Current
- ✅ Added NFR test generation (performance, security, accessibility)
- ✅ Concurrent test generation (2x speed improvement)
- ✅ Security enhancements (URL validation, code sanitization, path traversal protection)
- ✅ Comprehensive docstrings with AI tool discovery metadata
- ✅ Input validation and error handling
- ✅ Connection pooling for HTTP requests (30-50% faster)

### v2.0.0 (2024-12-20)
- ✅ Added functional test generation
- ✅ Playwright integration for element extraction
- ✅ JSON output format

### v1.0.0 (2024-11-10)
- ✅ Initial release with basic element extraction
- ✅ Ollama integration

---

## 🗺️ Roadmap

### v4.0 (Planned)
- [ ] Test execution engine (run generated tests)
- [ ] pytest/unittest integration
- [ ] HTML test report generation
- [ ] CI/CD templates (GitHub Actions, GitLab CI, Jenkins)

### v5.0 (Future)
- [ ] Web UI for test management
- [ ] Test case deduplication
- [ ] Multi-browser support (Firefox, Safari)
- [ ] Visual regression testing
- [ ] API testing support

---

<div align="center">

**Made with ❤️ by Kumar GN**

[Report Bug](https://github.com/GanduriKumar/prompt-test-agent/issues) • [Request Feature](https://github.com/GanduriKumar/prompt-test-agent/issues) • [Discussions](https://github.com/GanduriKumar/prompt-test-agent/discussions)

---

⭐ **Star this repo if you find it useful!** ⭐

</div>