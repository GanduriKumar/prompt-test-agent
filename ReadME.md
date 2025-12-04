# Prompt Test Agent

> **AI-powered test generation framework that automatically creates comprehensive test suites from any web page using local AI models.**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/Playwright-1.56-green.svg)](https://playwright.dev/)

## 🎯 What Does This Do?

This tool analyzes your web application and automatically generates:
- ✅ **Functional test cases** - Happy paths, negative cases, boundary conditions
- ⚡ **Performance tests** - Load time, response time, throughput benchmarks
- 🔒 **Security tests** - Authentication, input validation, OWASP checks
- ♿ **Accessibility tests** - WCAG compliance, keyboard navigation, ARIA
- 🎨 **Usability tests** - Form design, error messages, user experience
- 🛡️ **Reliability tests** - Error handling, resilience, failover

**No manual test writing** - Just provide a URL and business context, get JSON test specifications.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Usage Examples](#-usage-examples)
4. [Configuration](#-configuration)
5. [Project Architecture](#-project-architecture)
6. [Generated Output](#-generated-output)
7. [API Reference](#-api-reference)
8. [Troubleshooting](#-troubleshooting)
9. [Contributing](#-contributing)
10. [FAQ](#-faq)

---

## 🚀 Quick Start

### Prerequisites Checklist
- [ ] Python 3.8 or higher installed
- [ ] [Ollama](https://ollama.ai/) installed and running
- [ ] Three AI models downloaded (3 commands below)
- [ ] 10GB free disk space (for AI models)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/GanduriKumar/prompt-test-agent.git
cd prompt-test-agent

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Start Ollama (keep terminal open)
ollama serve

# 4. Download AI models (in new terminal)
ollama pull llama3.2              # Text model (~2GB)
ollama pull llama3.2-vision       # Vision model (~2GB)
ollama pull deepseek-coder:6.7b   # Code model (~4GB)

# 5. Create configuration
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VISION_MODEL=llama3.2-vision
CODING_MODEL=deepseek-coder:6.7b
EOF

# 6. Run test generator
python cua_agent.py
```

**First Run Output:**
```
Enter the URL to open: https://example.com
2025-01-15 10:30:45 - DEBUG - Opening URL: https://example.com
2025-01-15 10:30:47 - DEBUG - Extracting interactive elements
2025-01-15 10:30:49 - INFO - Generated 8 Functional Tests
2025-01-15 10:30:52 - INFO - Generated 12 NFR Tests
Tests saved to: generated_tests.json
```

---

## 📦 Installation

### Step 1: System Requirements

**Operating System:**
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian 11+)

**Python Version:**
```bash
python --version  # Should be 3.8 or higher
```

**Disk Space:**
- ~200MB for dependencies
- ~10GB for AI models
- ~500MB for Playwright browsers

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Installed packages:**
- `playwright~=1.56.0` - Browser automation (like Selenium but faster/more reliable)
- `requests~=2.32.5` - HTTP client for Ollama API communication
- `python-dotenv~=1.2.1` - Loads `.env` configuration files
- `certifi~=2025.11.12` - SSL certificate bundle (for HTTPS requests)
- `python-certifi-win32~=1.6.1` - Windows SSL support
- `ollama~=0.6.1` - Python client for Ollama (not actively used, can be removed)

### Step 3: Install Browser

```bash
playwright install chromium
```

Downloads Chromium browser (~170MB) used for:
- Opening web pages
- Extracting interactive elements
- Taking screenshots (if needed)
- Running generated automation code

### Step 4: Setup Ollama

**Install Ollama:**

| Platform | Command |
|----------|---------|
| macOS/Linux | `curl -fsSL https://ollama.ai/install.sh \| sh` |
| Windows | Download from [ollama.ai/download](https://ollama.ai/download) |

**Start Ollama Server:**
```bash
ollama serve
```
Leave this terminal running. Ollama listens on `http://localhost:11434`

**Download AI Models:**
```bash
# Text model for test generation
ollama pull llama3.2

# Vision model for screenshot analysis (optional)
ollama pull llama3.2-vision

# Code model for automation generation
ollama pull deepseek-coder:6.7b
```

**Verify installation:**
```bash
ollama list
# Should show: llama3.2, llama3.2-vision, deepseek-coder:6.7b
```

### Step 5: Configure Environment

Create `.env` file in project root:
```env
# Ollama server URL (default localhost)
OLLAMA_BASE_URL=http://localhost:11434

# Model names (must match 'ollama list' output)
OLLAMA_MODEL=llama3.2
VISION_MODEL=llama3.2-vision
CODING_MODEL=deepseek-coder:6.7b
```

**Note:** `.env` file is git-ignored for security.

---

## 💡 Usage Examples

### Example 1: Generate Tests for Login Page

```bash
python cua_agent.py
```

**Interactive Session:**
```
Enter the URL to open: https://myapp.com/login
2025-01-15 10:30:45 - DEBUG - Opening URL: https://myapp.com/login
2025-01-15 10:30:47 - DEBUG - Extracting interactive elements
2025-01-15 10:30:48 - DEBUG - Found 6 interactive elements
2025-01-15 10:30:49 - DEBUG - Generating functional tests
2025-01-15 10:30:55 - INFO - Generated Functional Tests: 8 tests
2025-01-15 10:30:56 - DEBUG - Generating NFR tests
2025-01-15 10:31:02 - INFO - Generated NFR Tests: 12 tests
Tests saved to generated_tests.json
```

**Time:** 30-60 seconds total

**Output:** `generated_tests.json` with 8 functional + 12 NFR test specifications

---

### Example 2: Programmatic Test Generation

**Use Case:** Integrate into CI/CD pipeline

```python
# test_generator.py
import asyncio
from cua_tools import generate_functional_tests, generate_nfr_tests

async def generate_tests_for_url(url, context):
    """Generate all tests for a given URL."""
    print(f"Analyzing: {url}")
    
    # Generate functional tests
    func_tests = await generate_functional_tests(url, context)
    print(f"✅ {len(func_tests)} functional tests")
    
    # Generate NFR tests with requirements
    nfr_reqs = {
        "performance": {"page_load": "< 2s"},
        "accessibility": {"wcag_level": "AA"}
    }
    nfr_tests = await generate_nfr_tests(url, context, nfr_reqs)
    print(f"✅ {len(nfr_tests)} NFR tests")
    
    return {"functional": func_tests, "nfr": nfr_tests}

# Run for multiple pages
pages = [
    ("https://myapp.com/login", "User authentication"),
    ("https://myapp.com/register", "User registration"),
    ("https://myapp.com/checkout", "E-commerce checkout")
]

for url, context in pages:
    tests = asyncio.run(generate_tests_for_url(url, context))
    # Save or process tests as needed
```

---

### Example 3: Element Discovery

**Use Case:** Understand page structure before test generation

```python
import asyncio
from cua_tools import get_interactive_elements

async def analyze_page_structure(url):
    """Extract and categorize interactive elements."""
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
        print(f"{tag.upper()}: {len(items)}")
        for item in items[:3]:  # Show first 3
            print(f"  • ID: {item.get('id', 'N/A')} | Text: {item.get('text', '')[:30]}")
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more")
        print()

# Run analysis
asyncio.run(analyze_page_structure("https://example.com"))
```

**Output:**
```
📊 Page Analysis: https://example.com

Total interactive elements: 15

INPUT: 4
  • ID: email | Text: 
  • ID: password | Text: 
  • ID: remember | Text: 
  ... and 1 more

BUTTON: 3
  • ID: login-btn | Text: Sign In
  • ID: forgot-pwd | Text: Forgot Password?
  • ID: signup-link | Text: Create Account

A: 8
  • ID: N/A | Text: Terms of Service
  • ID: N/A | Text: Privacy Policy
  ... and 6 more
```

---

### Example 4: Custom Test Requirements

**Use Case:** Generate tests with specific performance/security requirements

```python
import asyncio
from cua_tools import generate_nfr_tests

async def generate_strict_nfr_tests():
    """Generate NFR tests with strict requirements."""
    
    # Define strict requirements
    requirements = {
        "performance": {
            "page_load_time": "< 1.5s",
            "time_to_interactive": "< 2s",
            "first_contentful_paint": "< 800ms"
        },
        "security": {
            "https_only": True,
            "csrf_protection": True,
            "xss_prevention": True,
            "input_sanitization": True
        },
        "accessibility": {
            "wcag_level": "AAA",  # Highest level
            "keyboard_navigation": "full",
            "screen_reader": "compatible",
            "color_contrast": "7:1"
        }
    }
    
    tests = await generate_nfr_tests(
        url="https://myapp.com/payment",
        business_context="Payment processing page (PCI-DSS compliant)",
        nfr_expectations=requirements
    )
    
    # Display by category
    by_category = {}
    for test in tests:
        cat = test['category']
        by_category.setdefault(cat, []).append(test)
    
    for category, test_list in by_category.items():
        print(f"\n{category.upper()} Tests: {len(test_list)}")
        for test in test_list:
            print(f"  • {test['title']}")
            print(f"    Tools: {', '.join(test['tooling_suggestions'])}")

asyncio.run(generate_strict_nfr_tests())
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# === REQUIRED SETTINGS ===

# Ollama API endpoint
OLLAMA_BASE_URL=http://localhost:11434

# Text model for test generation
# Alternatives: mistral, mixtral:8x7b, llama3.1
OLLAMA_MODEL=llama3.2

# Vision model for image analysis (optional)
# Alternatives: llava, bakllava, llava-phi3
VISION_MODEL=llama3.2-vision

# Code model for automation generation (optional)
# Alternatives: codellama:13b, starcoder2
CODING_MODEL=deepseek-coder:6.7b
```

### Browser Configuration

**Viewport Size** (defined in [`cua_tools.py`](cua_tools.py)):
```python
VIEWPORT = {'width': 1280, 'height': 720}
```

To change, edit the constant in `cua_tools.py` (no hot reload - restart script).

**Headless Mode:**
- Test generation: Uses visible browser (`headless=False`) for debugging
- Code execution: Uses headless browser (`headless=True`) for speed

To change, modify `async def open_browser()` calls in `cua_tools.py`.

### Logging Configuration

**Default:** DEBUG level with timestamps (already configured in both scripts)

**To save logs to file**, add at top of `cua_agent.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_generation.log"),  # Save to file
        logging.StreamHandler()                       # Also print
    ]
)
```

**Logged information:**
- URL navigation and page loading
- Element extraction results
- AI model API calls
- Test generation progress
- File operations (JSON saving)

---

## 🏗️ Project Architecture

### File Structure

```
prompt-test-agent/
│
├── cua_agent.py              # Main entry point
│   └── Purpose: Orchestrates test generation workflow
│       - Prompts user for URL
│       - Calls functional test generator
│       - Calls NFR test generator  
│       - Saves results to JSON
│
├── cua_tools.py              # Core toolkit (all functions)
│   └── Purpose: Reusable automation functions
│       - Browser automation (open, navigate, extract)
│       - Element extraction (JavaScript evaluation)
│       - Test generation (functional + NFR)
│       - Code generation (Playwright automation)
│       - AI integration (Ollama API calls)
│
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (git-ignored)
├── .gitignore               # Files to exclude from git
├── LICENSE                  # MIT License
└── README.md                # This documentation
```

### Component Interaction

```
┌─────────────────┐
│   cua_agent.py  │  ← You run this
│   (Orchestrator)│
└────────┬────────┘
         │
         │ imports all functions from
         ▼
┌─────────────────────────────────────┐
│         cua_tools.py                │
│  (Function Library)                 │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Browser Functions           │   │
│  │ • open_browser()            │   │
│  │ • get_interactive_elements()│   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Test Generation             │   │
│  │ • build_functional_prompt() │   │
│  │ • build_nfr_prompt()        │   │
│  │ • generate_functional()     │   │
│  │ • generate_nfr()            │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Code Generation             │   │
│  │ • generate_automation_code()│   │
│  │ • execute_automation_code() │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ AI Integration              │   │
│  │ • generate_final_output()   │   │
│  │   (calls Ollama API)        │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         │ HTTP POST requests
         ▼
┌─────────────────┐
│  Ollama Server  │  ← Running on localhost:11434
│  (AI Models)    │
└─────────────────┘
```

### Data Flow

```
1. User Input
   └─> URL (e.g., https://example.com)
   └─> Business Context (hardcoded: "Search website")

2. Element Extraction
   └─> Playwright opens browser
   └─> JavaScript extracts: <a>, <button>, <input>, <textarea>, <select>
   └─> Returns: [{tag, type, id, name, text, placeholder, ariaLabel, role}, ...]

3. Test Generation (Parallel)
   
   ┌─────────────────────────┐   ┌────────────────────────┐
   │ Functional Tests        │   │ NFR Tests              │
   │                         │   │                        │
   │ • Prompt: "Generate     │   │ • Prompt: "Generate    │
   │   functional tests for  │   │   NFR tests covering   │
   │   these elements..."    │   │   performance,         │
   │                         │   │   security, a11y..."   │
   │ • Model: llama3.2       │   │ • Model: llama3.2      │
   │                         │   │                        │
   │ • Output: JSON array    │   │ • Output: JSON array   │
   └────────┬────────────────┘   └──────────┬─────────────┘
            │                               │
            └───────────┬───────────────────┘
                        │
                        ▼
4. Combine & Save
   └─> {
         "functional_tests": [...],
         "nfr_tests": [...]
       }
   └─> Save to generated_tests.json
```

### Key Design Decisions

**1. Separation of Concerns**
   - `cua_agent.py` = Workflow orchestration (what to do)
   - `cua_tools.py` = Reusable functions (how to do it)
   - Benefit: Functions can be imported and reused in other scripts

**2. Async/Await Architecture**
   - All browser operations use `async`/`await`
   - Benefit: Non-blocking I/O, faster execution
   - Note: Must run with `asyncio.run()` or in async context

**3. Prompt Engineering**
   - Separate prompt builder functions for functional vs NFR tests
   - JSON schema enforcement in prompts
   - Benefit: Consistent, parseable output from AI models

**4. JSON Output Format**
   - All test artifacts saved as structured JSON
   - Benefit: Easy to parse, version control, integrate with CI/CD

**5. Local AI Processing**
   - Uses Ollama (runs locally, no external API calls)
   - Benefit: Privacy, no rate limits, free usage

---

## 📄 Generated Output

### Primary Output: `generated_tests.json`

**Location:** Same directory as `cua_agent.py`

**Structure:**
```json
{
  "functional_tests": [
    {
      "id": "FUNC_001",
      "title": "User can search with valid query",
      "preconditions": [
        "User is on homepage",
        "Search box is visible"
      ],
      "steps": [
        "Click on search input field",
        "Enter search term 'AI automation'",
        "Click search button or press Enter"
      ],
      "expected_result": "Search results page displays relevant results",
      "tags": ["search", "happy-path", "critical"]
    }
  ],
  "nfr_tests": [
    {
      "id": "NFR_001",
      "category": "performance",
      "title": "Search page loads within 2 seconds",
      "description": "Measure time from search submission to results display",
      "acceptance_criteria": [
        "Page load time < 2000ms",
        "First Contentful Paint < 1000ms",
        "No JavaScript errors in console"
      ],
      "tooling_suggestions": ["Playwright", "Lighthouse", "WebPageTest"]
    },
    {
      "id": "NFR_002",
      "category": "accessibility",
      "title": "Search input has proper ARIA labels",
      "description": "Verify screen reader compatibility of search form",
      "acceptance_criteria": [
        "Input has aria-label or label element",
        "Button has accessible name",
        "Focus order is logical"
      ],
      "tooling_suggestions": ["axe-core", "NVDA", "JAWS"]
    }
  ]
}
```

### Field Descriptions

#### Functional Test Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier (auto-generated) | `"FUNC_001"` |
| `title` | string | One-line test description | `"User can login"` |
| `preconditions` | array | Required setup before test | `["User registered"]` |
| `steps` | array | Sequential actions | `["Click button", "Enter text"]` |
| `expected_result` | string | Pass criteria | `"Dashboard displayed"` |
| `tags` | array | Categories for filtering | `["login", "critical"]` |

#### NFR Test Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier | `"NFR_001"` |
| `category` | string | Test type | `"performance"`, `"security"`, `"accessibility"`, `"usability"`, `"reliability"` |
| `title` | string | One-line description | `"Page loads under 2s"` |
| `description` | string | Detailed explanation | `"Measure load time..."` |
| `acceptance_criteria` | array | Pass/fail conditions | `["Load < 2s", "No errors"]` |
| `tooling_suggestions` | array | Recommended tools | `["Lighthouse", "k6"]` |

### Additional Generated Files

| File | Created By | Purpose |
|------|-----------|---------|
| `generated_automation_code.py` | `generate_automation_code()` | Raw Playwright code (search automation) |
| `local_code.py` | `execute_automation_code()` | Wrapped code with async context |
| `screenshot.png` | `open_browser_capture_screen()` | Full-page screenshot (optional) |

**Note:** Only `generated_tests.json` is created by default in current implementation.

---

## 📚 API Reference

### Core Functions in `cua_tools.py`

#### Browser Functions

##### `async def get_interactive_elements(url: str) -> list[dict]`

**Purpose:** Extract all interactive elements from a web page

**Parameters:**
- `url` (str): Full URL to analyze

**Returns:** List of dictionaries with element metadata:
```python
[
    {
        "tag": "input",           # HTML tag name
        "type": "email",          # Type attribute (for inputs)
        "id": "email-field",      # ID attribute
        "name": "email",          # Name attribute
        "text": "",               # Visible text content
        "placeholder": "Email",   # Placeholder text
        "ariaLabel": "Email",     # ARIA label
        "role": None              # ARIA role
    },
    # ... more elements
]
```

**Usage:**
```python
elements = await get_interactive_elements("https://example.com")
inputs = [e for e in elements if e['tag'] == 'input']
```

**Note:** Opens visible browser, extracts elements via JavaScript, closes browser.

---

##### `async def open_browser(url: str) -> None`

**Purpose:** Open browser, navigate to URL, log title, close

**Parameters:**
- `url` (str): URL to navigate to

**Returns:** None

**Side Effects:**
- Launches Chromium (visible window)
- Sets viewport to 1280x720
- Waits for page load
- Logs page title to console
- Closes browser

**Usage:**
```python
await open_browser("https://example.com")
```

---

##### `async def open_browser_capture_screen(url: str, screenshot_path: str) -> tuple`

**Purpose:** Open browser, capture screenshot, return browser handles

**Parameters:**
- `url` (str): URL to navigate to
- `screenshot_path` (str): Where to save screenshot (e.g., `"screenshot.png"`)

**Returns:** `(browser, page)` tuple - both objects remain open

**⚠️ Warning:** Caller must close browser manually:
```python
browser, page = await open_browser_capture_screen("https://example.com", "out.png")
# ... do something with page ...
await browser.close()  # Required!
```

---

#### Test Generation Functions

##### `async def generate_functional_tests(url: str, business_context: str) -> list[dict]`

**Purpose:** Generate functional test cases for a web page

**Parameters:**
- `url` (str): Target URL
- `business_context` (str): Description of page purpose (helps AI generate relevant tests)

**Returns:** List of functional test dictionaries

**Example:**
```python
tests = await generate_functional_tests(
    url="https://myapp.com/login",
    business_context="User authentication page for e-commerce site"
)

# Returns:
# [
#   {
#     "id": "FUNC_001",
#     "title": "User can login with valid credentials",
#     "preconditions": ["User is registered"],
#     "steps": ["Enter email", "Enter password", "Click login"],
#     "expected_result": "User redirected to dashboard",
#     "tags": ["login", "authentication"]
#   },
#   # ... more tests
# ]
```

**Process:**
1. Extracts interactive elements
2. Builds prompt with elements + context
3. Calls Ollama API
4. Parses JSON response
5. Returns test array

---

##### `async def generate_nfr_tests(url: str, business_context: str, nfr_expectations: dict | None = None) -> list[dict]`

**Purpose:** Generate non-functional requirement test cases

**Parameters:**
- `url` (str): Target URL
- `business_context` (str): Page description
- `nfr_expectations` (dict, optional): Specific requirements

**NFR Expectations Format:**
```python
{
    "performance": {
        "page_load_time": "< 2s",
        "time_to_interactive": "< 3s"
    },
    "security": {
        "https_only": True,
        "csrf_protection": True
    },
    "accessibility": {
        "wcag_level": "AA"
    }
}
```

**Returns:** List of NFR test dictionaries

**Example:**
```python
tests = await generate_nfr_tests(
    url="https://myapp.com",
    business_context="Homepage",
    nfr_expectations={"performance": {"page_load": "< 2s"}}
)
```

---

#### Code Generation Functions

##### `def generate_automation_code(vision_elements: dict, url: str) -> str`

**Purpose:** Generate Playwright automation code (search functionality)

**Parameters:**
- `vision_elements` (dict): Page elements (currently unused in prompt)
- `url` (str): Target URL

**Returns:** Python code as string

**Behavior:**
- Generates code to fill search box with "AI based automation"
- Clicks search button
- Removes markdown code fences (```)
- Saves to `generated_automation_code.py`

**⚠️ Note:** Uses `CODING_MODEL` (deepseek-coder) - requires model to be pulled.

---

##### `async def execute_automation_code(actions_code: str, url: str) -> None`

**Purpose:** Execute Playwright automation code

**Parameters:**
- `actions_code` (str): Python code to execute
- `url` (str): Target URL

**⚠️ Security Warning:**
- Uses `exec()` which can run arbitrary code
- Only execute code from trusted sources
- Review generated code before execution

**Process:**
1. Wraps code in async context
2. Saves to `local_code.py`
3. Executes with `exec(local_code, globals())`

---

#### Helper Functions

##### `def build_functional_tests_prompt(url: str, elements: list, business_context: str) -> str`

**Purpose:** Build prompt for functional test generation

**Returns:** Formatted prompt string with JSON schema

---

##### `def build_nfr_tests_prompt(url: str, elements: list, business_context: str, nfr_expectations: dict | None) -> str`

**Purpose:** Build prompt for NFR test generation

**Returns:** Formatted prompt string with JSON schema

---

##### `def generate_final_output(prompt: str) -> str`

**Purpose:** Call Ollama API with prompt

**Parameters:**
- `prompt` (str): Text prompt for AI model

**Returns:** Raw response string from model

**API Call:**
```python
POST http://localhost:11434/api/generate
{
  "model": "llama3.2",
  "prompt": "...",
  "stream": False
}
```

---

##### `def encode_file_to_base64(screenshot_path: str) -> str`

**Purpose:** Convert image to base64 string (for vision models)

**Parameters:**
- `screenshot_path` (str): Path to image file

**Returns:** Base64-encoded string

---

##### `def extract_elements_from_image(encoded_image: str) -> str`

**Purpose:** Use vision model to extract elements from screenshot

**Parameters:**
- `encoded_image` (str): Base64-encoded image

**Returns:** JSON string with extracted elements

**⚠️ Note:** Currently not used in main workflow, but available for future features.

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue 1: Ollama Connection Error

**Symptoms:**
```
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Causes:**
1. Ollama not running
2. Wrong port in `.env`
3. Firewall blocking connection

**Solutions:**

**Step 1:** Check if Ollama is running
```bash
# Should return Ollama version
curl http://localhost:11434

# If not running:
ollama serve
```

**Step 2:** Verify `.env` configuration
```env
OLLAMA_BASE_URL=http://localhost:11434  # Default port
```

**Step 3:** Test with curl
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"test","stream":false}'
```

---

#### Issue 2: Model Not Found

**Symptoms:**
```
Error: model 'llama3.2' not found
```

**Solution:**
```bash
# List installed models
ollama list

# Install missing model
ollama pull llama3.2
ollama pull llama3.2-vision
ollama pull deepseek-coder:6.7b

# Verify installation
ollama list
```

**Expected Output:**
```
NAME                    ID              SIZE    MODIFIED
llama3.2:latest         abc123...       2.0 GB  2 days ago
llama3.2-vision:latest  def456...       2.1 GB  2 days ago
deepseek-coder:6.7b     ghi789...       3.8 GB  2 days ago
```

---

#### Issue 3: JSON Parsing Error

**Symptoms:**
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Causes:**
1. AI model not returning valid JSON
2. Model output wrapped in markdown
3. Model too small/weak for task

**Solutions:**

**Option 1:** Try different model
```bash
ollama pull mistral
```
Update `.env`:
```env
OLLAMA_MODEL=mistral
```

**Option 2:** Check model output manually
```python
from cua_tools import generate_final_output

prompt = "Generate JSON: {\"test\": \"value\"}"
output = generate_final_output(prompt)
print(f"Raw output: {output}")  # Inspect what model returns
```

**Option 3:** Increase model size
```bash
ollama pull llama3.1:70b  # Larger, more capable model
```

---

#### Issue 4: No Interactive Elements Found

**Symptoms:**
```
Generated 0 functional tests
```

**Causes:**
1. Page is static (no forms/buttons)
2. JavaScript-heavy page not fully loaded
3. Elements hidden/not rendered

**Solutions:**

**Check what was extracted:**
```python
elements = await get_interactive_elements("https://example.com")
print(f"Found {len(elements)} elements")
print(elements)  # Inspect actual output
```

**Increase wait time:**
Edit `cua_tools.py`, in `get_interactive_elements()`:
```python
await page.goto(url)
await page.wait_for_load_state('networkidle')  # Wait for all network activity
await page.wait_for_timeout(2000)  # Additional 2s wait
```

---

#### Issue 5: Playwright Browser Not Found

**Symptoms:**
```
playwright._impl._api_types.Error: Executable doesn't exist at C:\Users\...\chromium-1234\chrome-win\chrome.exe
```

**Solution:**
```bash
playwright install chromium
```

**Verify installation:**
```bash
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch()"
```

---

#### Issue 6: Slow Test Generation

**Symptoms:**
- Takes > 2 minutes per generation
- System freezes during generation

**Causes:**
1. AI model too large for hardware
2. No GPU acceleration
3. Too many elements on page

**Solutions:**

**Use smaller/faster model:**
```bash
ollama pull llama3.2:8b  # Smaller variant
```

**Check system resources:**
```bash
# Monitor RAM/CPU during generation
# Windows:
taskmgr

# Linux/Mac:
htop
```

**Optimize hardware:**
- Close other applications
- Ensure 8GB+ RAM available
- Use GPU if available (Ollama auto-detects)

---

#### Issue 7: Generated Code Execution Fails

**Symptoms:**
```
NameError: name 'async_playwright' is not defined
SyntaxError: invalid syntax
```

**Causes:**
1. Generated code malformed
2. Missing imports
3. Code generation model weak

**Solutions:**

**Review generated code:**
```python
# Check generated_automation_code.py
with open("generated_automation_code.py") as f:
    print(f.read())
```

**Use better coding model:**
```bash
ollama pull codellama:13b
```
Update `.env`:
```env
CODING_MODEL=codellama:13b
```

---

### Debug Mode

**Enable verbose logging:**

Add to top of `cua_agent.py`:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
```

**Inspect generated prompts:**

Add before API call in `cua_tools.py`:
```python
def generate_final_output(prompt: str) -> str:
    print(f"\n=== PROMPT ===\n{prompt}\n=============\n")  # Add this
    payload = {...}
```

---

## 🤝 Contributing

### How to Contribute

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/prompt-test-agent.git
   ```
3. **Create feature branch:**
   ```bash
   git checkout -b feature/my-improvement
   ```
4. **Make changes** and test
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add support for API testing"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/my-improvement
   ```
7. **Open Pull Request** on GitHub

### Contribution Ideas

**🟢 Easy (Good First Issue)**
- Add more AI model examples in README
- Improve error messages
- Add validation for URLs
- Create example test outputs

**🟡 Medium**
- Add CLI arguments (`--url`, `--context`, `--output`)
- Support Firefox/Safari browsers
- Export tests to CSV/XML format
- Add test case deduplication

**🔴 Advanced**
- Implement test execution engine
- Add pytest integration
- Create web UI for test management
- Docker containerization
- CI/CD pipeline integration

### Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Setup Ollama and models
ollama serve
ollama pull llama3.2 llama3.2-vision deepseek-coder:6.7b

# Run tests
python cua_agent.py
```

### Code Style Guidelines

- Follow PEP 8 (use `black` formatter)
- Add type hints for function parameters
- Write comprehensive docstrings
- Include AI-discovery metadata in docstrings
- Add logging for key operations
- Update README for new features

---

## ❓ FAQ

**Q: Do I need internet for test generation?**

A: Only during initial setup (downloading models). After that, everything runs locally.

---

**Q: How much disk space do AI models need?**

A: ~10GB total:
- `llama3.2`: ~2GB
- `llama3.2-vision`: ~2GB  
- `deepseek-coder:6.7b`: ~4GB

---

**Q: Can I use different AI models?**

A: Yes! Any Ollama-compatible model. Edit `.env`:
```env
OLLAMA_MODEL=mistral
VISION_MODEL=llava
CODING_MODEL=codellama
```

---

**Q: Does this execute tests or just generate them?**

A: Currently **generates test specifications only**. You'll need to:
1. Export tests to your test framework (pytest, unittest)
2. Implement test logic based on specifications
3. Integrate with CI/CD

Test execution planned for v4.0.

---

**Q: Is my data sent to external servers?**

A: **No.** All AI processing happens locally via Ollama. No external API calls unless you configure a remote Ollama server.

---

**Q: Can I use this in CI/CD pipelines?**

A: **Yes!** Example:
```yaml
# .github/workflows/test-generation.yml
- name: Generate Tests
  run: |
    python cua_agent.py <<< "https://myapp.com"
    cat generated_tests.json
```

---

**Q: What's the business context for?**

A: Helps AI understand page purpose for better test generation:
- ❌ Generic: "Search website"
- ✅ Specific: "E-commerce product search for electronics store"

Currently hardcoded in `cua_agent.py` line 14 - can be parameterized.

---

**Q: Can I generate tests for authenticated pages?**

A: Not directly. Workarounds:
1. Manually login first, then run on authenticated page
2. Modify `get_interactive_elements()` to include login steps
3. Use Playwright's `storageState` to save cookies

---

**Q: Why is test generation slow?**

A: AI inference time depends on:
- Model size (larger = slower but better quality)
- Hardware (CPU vs GPU)
- Prompt complexity

Typical times:
- Fast (8B model, GPU): 5-10 seconds
- Medium (13B model, CPU): 20-40 seconds
- Slow (70B model, CPU): 60-120 seconds

---

## 📝 License

MIT License - see [`LICENSE`](LICENSE) file

**TL;DR:** Free to use, modify, distribute. No warranty provided.

---

## 👤 Author

**GanduriKumar**
- GitHub: [@GanduriKumar](https://github.com/GanduriKumar)

---

## 🙏 Acknowledgments

- **[Playwright](https://playwright.dev/)** - Reliable browser automation
- **[Ollama](https://ollama.ai/)** - Local AI inference (no external APIs)
- **[Meta LLaMA](https://ai.meta.com/llama/)** - Open-source language models
- **[DeepSeek](https://github.com/deepseek-ai)** - Code generation models

---

## 🔄 Version History

- **v3.0.0** (2025-12-04s) - Added NFR and functions test generation


---

<div align="center">

**Made with ❤️ by KumarGN**

[Report Bug](https://github.com/GanduriKumar/prompt-test-agent/issues) • [Request Feature](https://github.com/GanduriKumar/prompt-test-agent/issues) • [Documentation](https://github.com/GanduriKumar/prompt-test-agent)

---

⭐ **Star this repo if you find it useful!**

</div>