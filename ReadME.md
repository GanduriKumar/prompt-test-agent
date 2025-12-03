# Prompt Test Agent

A Python-based intelligent web automation framework that combines Playwright browser automation with Ollama AI models for vision-based UI element extraction and autonomous test generation.

## Overview

This project provides an AI-powered automation agent that can:
- **Capture** web page screenshots using Playwright
- **Analyze** UI elements using vision-capable AI models (Ollama)
- **Generate** automation code dynamically based on detected elements
- **Execute** generated automation scripts autonomously

## Features

- 🌐 Async browser control with Playwright Chromium
- 📸 Full-page screenshot capture with configurable viewport (1280x720)
- 👁️ Vision-based UI element extraction using Ollama multimodal models
- 🤖 AI-powered automation code generation
- ⚡ Dynamic code execution engine
- 🔍 HTML element detection (tag, id, class, text)
- 📝 Natural language instruction processing
- 🎯 Non-headless browser mode for visual debugging
- 🔐 Environment-based configuration management
- 📊 Comprehensive debug logging

## Project Structure

```
.
├── cua_agent.py           # Main autonomous agent orchestrator
├── cua_tools.py          # Core toolkit: browser, vision, code generation
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License
├── ReadME.md            # Project documentation
├── .env                 # Environment configuration (not tracked)
├── .gitignore          # Git ignore rules
├── __pycache__/        # Python bytecode cache (not tracked)
└── .idea/              # PyCharm IDE configuration
    ├── .gitignore
    ├── misc.xml
    ├── modules.xml
    ├── prompt-test-agent.iml
    ├── vcs.xml
    ├── workspace.xml
    └── inspectionProfiles/
        ├── profiles_settings.xml
        └── Project_Default.xml
```

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Vision-capable Ollama model (e.g., `llava`, `bakllava`, `llama3.2-vision`)
- Chromium browser (installed via Playwright)
- Windows OS (for `python-certifi-win32` support, optional for other platforms)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KumarGN/prompt-test-agent.git
   cd prompt-test-agent
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   # Base URL for Ollama server
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Model for code generation (text-based)
   OLLAMA_MODEL=llama3.2
   
   # Model for vision/image analysis
   VISION_MODEL=llama3.2-vision
   ```

5. **Verify Ollama is running:**
   ```bash
   ollama serve
   ```

6. **Download required models:**
   ```bash
   ollama pull llama3.2
   ollama pull llama3.2-vision
   ```

## Usage

### Autonomous Agent Mode (Main)

Run the intelligent automation agent:

```bash
python cua_agent.py
```

**Automated Workflow:**
1. Enter the target URL when prompted
2. Agent captures full-page screenshot
3. Vision model extracts UI elements (inputs, buttons, etc.)
4. Code generation model creates Playwright automation code
5. Generated code is executed automatically
6. All steps are logged with DEBUG level detail

**Example Session:**
```
Enter the URL to open: https://example.com/login
2025-01-15 10:30:45 - DEBUG - Opening URL: https://example.com/login
2025-01-15 10:30:47 - DEBUG - Screenshot saved as screenshot.png
2025-01-15 10:30:48 - DEBUG - Encoding file screenshot.png to base64
2025-01-15 10:30:49 - DEBUG - Extracting elements from encoded image
2025-01-15 10:30:52 - DEBUG - Extracted Elements: [{"tag": "input", "id": "email", ...}]
2025-01-15 10:30:53 - DEBUG - Generating automation code for vision elements
2025-01-15 10:30:56 - DEBUG - Generated Automation Code: async def run()...
2025-01-15 10:30:57 - DEBUG - Executing automation code
```

### Programmatic Usage

#### Example 1: Vision-Based Element Extraction

```python
import asyncio
from cua_tools import open_browser_capture_screen, encode_file_to_base64, extract_elements_from_image

async def analyze_page():
    # Capture screenshot
    browser, page = await open_browser_capture_screen(
        url="https://example.com",
        screenshot_path="page.png"
    )
    
    # Extract elements using vision model
    encoded_image = encode_file_to_base64("page.png")
    elements = extract_elements_from_image(encoded_image)
    
    print(f"Detected elements: {elements}")
    await browser.close()

asyncio.run(analyze_page())
```

#### Example 2: Generate and Execute Automation

```python
from cua_tools import generate_automation_code, execute_automation_code

# Generate code based on extracted elements
elements = [
    {"tag": "input", "id": "username", "class": "form-control", "text": ""},
    {"tag": "button", "id": "submit", "class": "btn-primary", "text": "Login"}
]

automation_code = generate_automation_code(elements)
print(automation_code)

# Execute generated code
await execute_automation_code(automation_code, "https://example.com/login")
```

#### Example 3: Simple Browser Navigation

```python
from cua_tools import open_browser

# Opens browser, navigates to URL, logs title, then closes
await open_browser("https://example.com")
```

## Key Components

### [`cua_agent.py`](cua_agent.py)

Main autonomous agent orchestrator that coordinates the complete automation workflow:

**Workflow Steps:**
1. **User Input:** Prompts for target URL
2. **Screenshot Capture:** Opens browser and captures full-page screenshot
3. **Element Extraction:** Uses vision model to detect UI elements
4. **Code Generation:** Creates Playwright automation code
5. **Execution:** Runs generated code against the target page

**Key Features:**
- Async/await architecture
- Comprehensive logging at each step
- Error handling and validation
- Clean resource management

### [`cua_tools.py`](cua_tools.py)

Core toolkit module providing all automation capabilities:

#### Browser Automation Functions

**[`open_browser(url)`](cua_tools.py)**
- Launches Chromium in non-headless mode (async)
- Sets viewport to 1280x720
- Navigates to specified URL
- Waits for page load
- Logs page title
- Automatically closes browser

**[`open_browser_capture_screen(url, screenshot_path)`](cua_tools.py)**
- Async browser launch with viewport configuration
- Full-page screenshot capture
- Returns live browser and page objects
- **Important:** Caller must close browser manually

**Configuration:**
```python
VIEWPORT = {'width': 1280, 'height': 720}
```

#### AI Integration Functions

**[`encode_file_to_base64(screenshot_path)`](cua_tools.py)**
- Encodes image files to base64 strings
- Returns UTF-8 encoded string without newlines
- Includes debug logging
- Handles binary file reading

**[`extract_elements_from_image(encoded_image)`](cua_tools.py)**
- Uses vision model to analyze screenshots
- Extracts HTML-like UI elements
- Returns JSON array of objects with fields:
  - `tag`: HTML tag name (e.g., "input", "button")
  - `id`: Element ID attribute
  - `class`: CSS class names
  - `text`: Text content
- Posts to Ollama `/api/generate` endpoint
- Enforces JSON response format

**Request Structure:**
```python
{
    "model": VISION_MODEL,
    "prompt": "Extract all HTML elements...",
    "stream": False,
    "images": [encoded_image],
    "format": "json"
}
```

**[`generate_automation_code(vision_elements)`](cua_tools.py)**
- Generates Python Playwright automation code
- Uses text-based Ollama model
- Focuses on form filling and button clicking
- Returns executable Python code as string
- Designed for AI agent discovery and autonomous workflows

**Prompt Template:**
```python
f"You are an automation agent. The user interface contains:{vision_elements}. 
Generate Python Playwright code to fill out the email and password fields 
and click the 'Log In' button.
Output only the Python code for the actions, no explanation.
Provide only the code without any explanations."
```

**[`execute_automation_code(actions_code, url)`](cua_tools.py)**
- Dynamically executes generated Playwright code
- Runs in headless mode for performance
- Wraps code in async context manager
- Uses `exec()` with globals scope
- Automatically handles browser lifecycle
- **Security Note:** Only execute trusted code

**Generated Code Structure:**
```python
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"{url}")
        {actions_code}  # Injected code here
        await browser.close()
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| playwright | ~1.56.0 | Async browser automation and testing framework |
| ollama | ~0.6.1 | Local AI model integration (not directly used in tools) |
| python-dotenv | ~1.2.1 | Environment variable management from `.env` files |
| certifi | ~2025.11.12 | SSL certificate validation bundle |
| python-certifi-win32 | ~1.6.1 | Windows-specific SSL certificate support |
| requests | ~2.32.5 | HTTP library for Ollama API calls |

See [`requirements.txt`](requirements.txt) for exact versions.

## Configuration

### Environment Variables

Configure in `.env` file (not tracked in version control):

```env
# Ollama server base URL
OLLAMA_BASE_URL=http://localhost:11434

# Text-based model for code generation
# Examples: llama3.2, mistral, codellama
OLLAMA_MODEL=llama3.2

# Vision-capable model for image analysis
# Examples: llama3.2-vision, llava, bakllava
VISION_MODEL=llama3.2-vision
```

**Required Models:**
- **VISION_MODEL:** Must support image input (multimodal)
- **OLLAMA_MODEL:** Can be text-only, optimized for code generation

### Logging Configuration

All modules use consistent DEBUG-level logging:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)
```

**Logged Events:**
- URL navigation
- Screenshot capture and saving
- File encoding operations
- Element extraction results
- Code generation output
- Automation execution
- All API requests/responses

### Viewport Settings

Standardized browser viewport in [`cua_tools.py`](cua_tools.py):

```python
VIEWPORT = {'width': 1280, 'height': 720}
```

## AI Agent Discovery

This framework is designed for AI agent discoverability and autonomous automation:

**Tags:** `#autonomous-agent` `#vision-ai` `#code-generation` `#playwright` `#ollama` `#multimodal` `#web-automation` `#dynamic-execution` `#ui-testing` `#computer-use-agent`

**AI Tool Metadata (Embedded in Docstrings):**
- Function discovery tags for automated tooling
- Input/output schemas documented
- Purpose and side effects clearly stated
- Failure modes and error handling described

**Supported AI Tasks:**
- Autonomous UI interaction
- Vision-based element detection
- Dynamic test case generation
- Form automation
- Login sequence automation
- Regression testing
- Accessibility auditing

## Use Cases & Examples

### Use Case 1: Autonomous Login Automation

```python
import asyncio
from cua_tools import *

async def auto_login():
    # Step 1: Capture login page
    browser, page = await open_browser_capture_screen(
        "https://example.com/login",
        "login.png"
    )
    await browser.close()
    
    # Step 2: Extract form elements
    encoded = encode_file_to_base64("login.png")
    elements = extract_elements_from_image(encoded)
    print(f"Found elements: {elements}")
    
    # Step 3: Generate automation code
    code = generate_automation_code(elements)
    print(f"Generated code:\n{code}")
    
    # Step 4: Execute automation
    await execute_automation_code(code, "https://example.com/login")

asyncio.run(auto_login())
```

### Use Case 2: Form Field Discovery

```python
# Extract all input fields from a form
encoded_image = encode_file_to_base64("form_screenshot.png")
fields = extract_elements_from_image(encoded_image)

# Filter for input elements
input_fields = [f for f in fields if f['tag'] == 'input']
print(f"Found {len(input_fields)} input fields:")
for field in input_fields:
    print(f"  - {field['id']}: {field.get('text', 'N/A')}")
```

### Use Case 3: Visual Regression Testing

```python
async def compare_pages():
    # Capture baseline
    await open_browser_capture_screen("https://example.com", "baseline.png")
    
    # Capture current state
    await open_browser_capture_screen("https://example.com", "current.png")
    
    # Extract elements from both
    baseline_elements = extract_elements_from_image(
        encode_file_to_base64("baseline.png")
    )
    current_elements = extract_elements_from_image(
        encode_file_to_base64("current.png")
    )
    
    # Compare (custom logic)
    if baseline_elements != current_elements:
        print("⚠️ UI changes detected!")
    else:
        print("✅ No changes detected")
```

### Use Case 4: Dynamic Test Generation

```python
# Generate tests for any web form
async def generate_form_tests(url):
    browser, page = await open_browser_capture_screen(url, "form.png")
    await browser.close()
    
    elements = extract_elements_from_image(encode_file_to_base64("form.png"))
    test_code = generate_automation_code(elements)
    
    # Save to file for review
    with open("generated_test.py", "w") as f:
        f.write(test_code)
    
    print(f"Test generated and saved to generated_test.py")
```

## Troubleshooting

### Common Issues

#### 1. **Ollama Connection Errors**
```
requests.exceptions.ConnectionError: Connection refused
```
**Solution:**
- Ensure Ollama is running: `ollama serve`
- Verify `OLLAMA_BASE_URL` in `.env` matches server address
- Check firewall settings

#### 2. **Vision Model Not Found**
```
Error: model 'llama3.2-vision' not found
```
**Solution:**
```bash
ollama pull llama3.2-vision
ollama list  # Verify installation
```

#### 3. **Playwright Browser Not Found**
```
playwright._impl._api_types.Error: Executable doesn't exist
```
**Solution:**
```bash
playwright install chromium
```

#### 4. **Async Function Not Awaited**
```
RuntimeWarning: coroutine 'open_browser' was never awaited
```
**Solution:**
- Use `await` keyword: `await open_browser(url)`
- Or run with: `asyncio.run(open_browser(url))`

#### 5. **JSON Decode Error from Vision Model**
```
json.JSONDecodeError: Expecting value
```
**Solution:**
- Model may not be returning valid JSON
- Try different vision model: `ollama pull llava`
- Check model supports `format: "json"` parameter

#### 6. **Screenshot File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory: 'screenshot.png'
```
**Solution:**
- Ensure write permissions in current directory
- Use absolute paths: `os.path.abspath("screenshot.png")`
- Check disk space

#### 7. **Dynamic Code Execution Errors**
```
NameError: name 'page' is not defined
```
**Solution:**
- Generated code may be malformed
- Review `automation_code` before execution
- Improve prompt in `generate_automation_code()`

### Debug Mode

All modules already use `DEBUG` level logging. To capture to file:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
```

## Architecture & Design

### Component Interaction Flow

```
User Input (URL)
    ↓
[cua_agent.py] Main Orchestrator
    ↓
[cua_tools.py] → open_browser_capture_screen()
    ↓
Screenshot (PNG file)
    ↓
[cua_tools.py] → encode_file_to_base64()
    ↓
Base64 String
    ↓
[cua_tools.py] → extract_elements_from_image()
    ↓
Ollama Vision Model (VISION_MODEL)
    ↓
UI Elements (JSON)
    ↓
[cua_tools.py] → generate_automation_code()
    ↓
Ollama Text Model (OLLAMA_MODEL)
    ↓
Python Code (String)
    ↓
[cua_tools.py] → execute_automation_code()
    ↓
Dynamic exec() Execution
    ↓
Automated Browser Actions
```

### Key Design Patterns

- **Async/Await:** All browser operations use async API
- **Tool-Based Architecture:** Modular functions for agent composition
- **Vision-First:** UI understanding through multimodal AI
- **Code Generation:** Self-modifying automation
- **Dynamic Execution:** Runtime code compilation and execution

### Security Considerations

⚠️ **IMPORTANT:**
- `execute_automation_code()` uses `exec()` which can execute arbitrary code
- **Only use with trusted AI models and validated inputs**
- Consider sandboxing execution environment
- Review generated code before execution in production

Other considerations:
- `.env` file not tracked (contains configuration)
- Local Ollama instance (no external API calls)
- Screenshots may contain sensitive information
- Generated code has full Playwright capabilities

## Development

### For Contributors

1. **Fork and clone** the repository
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. **Configure `.env`:**
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   VISION_MODEL=llama3.2-vision
   ```
5. **Test installation:**
   ```bash
   python cua_agent.py
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include comprehensive docstrings with AI metadata
- Add logging statements for key operations
- Use async/await for I/O operations
- Update README for new features

### Testing

Manual testing via [`cua_agent.py`](cua_agent.py). Future additions:
- Unit tests for individual tools
- Integration tests for full workflow
- Mock Ollama responses for CI/CD

## Roadmap

- [ ] Add unit test suite
- [ ] Support multiple browser engines (Firefox, WebKit)
- [ ] Configurable viewport via CLI args
- [ ] Batch processing multiple URLs
- [ ] Export results to JSON/CSV
- [ ] Web UI for agent management
- [ ] Docker containerization
- [ ] Sandboxed code execution environment
- [ ] Human-in-the-loop approval for generated code
- [ ] Test result reporting and analytics
- [ ] Integration with test frameworks (pytest, unittest)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Areas

- Add new tool functions to [`cua_tools.py`](cua_tools.py)
- Improve prompt engineering for better code generation
- Add support for more UI element types
- Enhance error handling and validation
- Write documentation and examples
- Add test coverage

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

**Copyright (c) 2025 KumarGN**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## Author

**KumarGN**
- GitHub: [@KumarGN](https://github.com/KumarGN)

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable async browser automation
- Powered by [Ollama](https://ollama.ai/) for local multimodal AI inference
- Inspired by Computer Use Agent (CUA) patterns and autonomous agent architectures
- Uses [requests](https://requests.readthedocs.io/) for HTTP communication
- Configuration managed by [python-dotenv](https://github.com/theskumar/python-dotenv)

## Technical Notes

### Performance

- Async operations allow concurrent execution
- Screenshots saved to disk (not held in memory)
- Vision model inference time varies (2-10 seconds typical)
- Code generation typically < 5 seconds
- Browser instances must be manually closed to free resources

### Limitations

- Requires local Ollama installation
- Vision model accuracy depends on model quality
- Generated code may need validation
- Limited to Chromium browser currently
- No built-in retry logic for API failures

### Future Enhancements

- Multi-model ensemble for better accuracy
- Streaming responses from Ollama
- Caching of vision analysis results
- Parallel screenshot processing
- Custom element detection rules

---

**Note:** This is an active development project focused on autonomous AI agents and vision-based automation. APIs and functionality may evolve rapidly.

**Last Updated:** 2025-12-03 
**Version:** 2.0.0 (Vision-First Architecture)