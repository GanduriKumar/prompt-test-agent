# Quick Reference: Multi-Provider LLM Setup

## 🚀 Quick Start Commands

### Ollama (Local, Free)
```bash
# Install
curl -fsSL https://ollama.ai/install.sh | sh

# Start
ollama serve &

# Download models
ollama pull llama3.2
ollama pull llama3.2-vision
ollama pull deepseek-coder:6.7b

# Configure
cat > .env << EOF
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_VISION_MODEL=llama3.2-vision
LLM_CODING_MODEL=deepseek-coder:6.7b
OLLAMA_BASE_URL=http://localhost:11434
EOF

# Test
python test_llm_providers.py
```

### OpenAI
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_VISION_MODEL=gpt-4-vision-preview
LLM_CODING_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-key-here
EOF

# Test
python test_llm_providers.py
```

### Anthropic Claude
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
LLM_VISION_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=sk-ant-your-key-here
EOF

# Test
python test_llm_providers.py
```

### Google Gemini
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=google
LLM_MODEL=gemini-pro
LLM_VISION_MODEL=gemini-pro-vision
GOOGLE_API_KEY=your-key-here
EOF

# Test
python test_llm_providers.py
```

### Azure OpenAI
```bash
# Configure
cat > .env << EOF
LLM_PROVIDER=azure
LLM_MODEL=gpt-4
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
EOF

# Test
python test_llm_providers.py
```

---

## 📊 Provider Comparison

| Feature | Ollama | OpenAI | Anthropic | Google | Azure |
|---------|--------|--------|-----------|--------|-------|
| **Cost** | Free | $$$ | $$$ | $ | $$$ |
| **Privacy** | 100% Local | Cloud | Cloud | Cloud | Enterprise |
| **Setup** | Medium | Easy | Easy | Easy | Hard |
| **Speed** | Slow-Medium | Fast | Fast | Fast | Fast |
| **Quality** | Good | Excellent | Excellent | Good | Excellent |
| **API Key** | No | Yes | Yes | Yes | Yes |
| **Best For** | Dev/Testing | Production | Production | Cost-conscious | Enterprise |

---

## 🔧 Common Issues

### "Provider not found"
```bash
# Check provider name
grep LLM_PROVIDER .env
# Must be: ollama, openai, anthropic, google, or azure
```

### "API key not found"
```bash
# Check API key is set
grep API_KEY .env
# Make sure key is not empty or placeholder
```

### "Connection refused" (Ollama)
```bash
# Start Ollama server
ollama serve

# Check it's running
curl http://localhost:11434
```

### "Model not found" (Ollama)
```bash
# List installed models
ollama list

# Download missing model
ollama pull llama3.2
```

### Rate limit errors
```bash
# Solution 1: Add delays
# Solution 2: Use Ollama (no limits)
# Solution 3: Upgrade API plan
```

---

## 📈 Performance Guide

### Speed (seconds per test generation)

**Ollama:**
- CPU: 30-60s
- GPU: 10-20s

**Cloud Providers:**
- GPT-4: 15-30s
- GPT-3.5: 5-10s
- Claude: 10-25s
- Gemini: 8-15s

### Cost (per URL tested)

**Ollama:** $0 (free)

**Cloud Providers:**
- GPT-4: $0.20-$0.50
- GPT-3.5: $0.02-$0.05
- Claude Opus: $0.30-$0.70
- Claude Sonnet: $0.06-$0.15
- Gemini: $0.02-$0.05

### Quality (subjective)

1. GPT-4 ⭐⭐⭐⭐⭐
2. Claude 3 Opus ⭐⭐⭐⭐⭐
3. Claude 3 Sonnet ⭐⭐⭐⭐
4. GPT-3.5 ⭐⭐⭐⭐
5. Gemini Pro ⭐⭐⭐⭐
6. Ollama (llama3.2) ⭐⭐⭐

---

## 🎯 Recommendations

**For Learning/Testing:**
→ Use Ollama (free, no limits)

**For Production (Best Quality):**
→ Use OpenAI GPT-4 or Claude 3 Opus

**For Production (Cost-Effective):**
→ Use Google Gemini or GPT-3.5

**For Enterprise:**
→ Use Azure OpenAI (security, compliance)

**For Privacy-Sensitive Projects:**
→ Use Ollama (100% local)

---

## 🔗 Quick Links

- [Detailed Setup Guide](LLM_PROVIDER_GUIDE.md)
- [Test Your Setup](test_llm_providers.py)
- [Environment Example](.env.example)
- [Main README](README.md)

---

## 💡 Pro Tips

1. **Start local, scale to cloud:**
   - Dev: Ollama
   - Staging: Gemini/GPT-3.5
   - Prod: GPT-4/Claude

2. **Use different models for different tasks:**
   ```env
   LLM_MODEL=gpt-4-turbo-preview      # Best for test generation
   LLM_VISION_MODEL=gpt-4-vision      # Required for vision
   LLM_CODING_MODEL=gpt-3.5-turbo     # Cheaper for code
   ```

3. **Monitor costs:**
   - Set usage alerts in provider dashboard
   - Cache results to avoid re-generation
   - Use cheaper models for prototyping

4. **Optimize for speed:**
   - Use GPU with Ollama
   - Use GPT-3.5 or Claude Haiku
   - Enable parallel processing

5. **Fallback strategy:**
   ```python
   # Try cloud first, fallback to local
   try:
       provider = LLMProvider(provider="openai")
   except:
       provider = LLMProvider(provider="ollama")
   ```

---

## 🆘 Getting Help

1. **Run diagnostics:**
   ```bash
   python test_llm_providers.py
   ```

2. **Enable debug logging:**
   ```bash
   export LOG_LEVEL=DEBUG
   python cua_agent.py
   ```

3. **Check documentation:**
   - [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md) - Detailed setup
   - [README.md](README.md) - General usage
   - [.env.example](.env.example) - Configuration examples

4. **Common commands:**
   ```bash
   # Verify Python version
   python --version

   # Check dependencies
   pip list | grep -E "openai|anthropic|google"

   # Test Ollama
   ollama list
   curl http://localhost:11434

   # Check environment
   cat .env
   ```
