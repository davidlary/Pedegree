# Currently Available AI Models - Practical Guide

*Last updated: 2025-07-30T14:31:43.860570*

This document shows only the AI models **currently available to you** based on your API keys and installed local models.

## 🎯 Quick Summary

**Total Available Models: 69**
- 📡 **Hosted Models**: 65 (from 3 providers with API keys)
- 💻 **Local Models**: 4 (installed via Ollama)

## 🗝️ Available Providers

- **OpenAI**: ✅ Available - GPT-4o, O1, ChatGPT models\n- **Anthropic**: ✅ Available - Claude 3.5 Sonnet, Opus, Haiku\n- **xAI**: ✅ Available - Grok-2, Grok-3, Grok-4 models\n- **Google**: ❌ No API key\n
## 💻 Local Models (Ollama)

**Installed Models: 4**

- **llama-3-8b**: 6GB ⭐⭐⭐⭐ - Balanced reasoning + offline privacy, efficient on Apple Silicon\n- **mistral-7b**: 6GB ⭐⭐⭐⭐⭐ - Code + logic tasks, very fast, excellent for development\n- **code-llama-7b**: 8GB ⭐⭐⭐⭐ - Specialized for code generation and completion\n- **phi-3-mini**: 3GB ⭐⭐⭐⭐⭐ - Efficient for small reasoning/code tasks, very lightweight\n
## 📡 Hosted Models Breakdown

### Openai (51 models)\n\n**Budget Models (<$1/1K tokens):**\n- gpt-3.5-turbo: $0.500/1K tokens\n- gpt-3.5-turbo-1106: $0.500/1K tokens\n- gpt-3.5-turbo-0125: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- gpt-3.5-turbo-instruct: $1.500/1K tokens\n- gpt-3.5-turbo-instruct-0914: $1.500/1K tokens\n- gpt-4o: $2.500/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- gpt-4-0613: $30.000/1K tokens\n- gpt-4: $30.000/1K tokens\n- gpt-4o-realtime-preview-2025-06-03: $6.000/1K tokens\n\n### Anthropic (5 models)\n\n**Budget Models (<$1/1K tokens):**\n- claude-3-haiku-20240307: $0.250/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- claude-3-5-sonnet-20241022: $3.000/1K tokens\n- claude-3-5-sonnet-20240620: $3.000/1K tokens\n- claude-3-sonnet-20240229: $3.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- claude-3-opus-20240229: $15.000/1K tokens\n\n### Xai (9 models)\n\n**Budget Models (<$1/1K tokens):**\n- grok-3-mini: $1.000/1K tokens\n- grok-3-mini-fast: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- grok-2-1212: $2.000/1K tokens\n- grok-2-vision-1212: $2.000/1K tokens\n- grok-2-image-1212: $2.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- grok-3: $12.000/1K tokens\n- grok-3-fast: $8.000/1K tokens\n- grok-4-0709: $8.000/1K tokens\n\n
## 🚀 Quick Start Commands

### Local Models (Free)
```bash
# Use your installed local models
ollama run llama3.1:8b "Write a Python function"
ollama run mistral:7b "Explain quantum physics"  
ollama run codellama:7b "Debug this code"
ollama run phi3:mini "Quick question"
```

### Hosted Models (API Key Required)
```python
# Use the IntelligentLLMRouter for automatic selection
from IntelligentLLMRouter import IntelligentLLMRouter

router = IntelligentLLMRouter()
result = router.route_request("Your prompt here")
print(f"Recommended: {result['recommended_model']}")
```

## 📊 Cost Comparison (Available Models Only)

**Cheapest Options:**
1. **local/code-llama-7b**: Free (local)\n2. **local/llama-3-8b**: Free (local)\n3. **local/mistral-7b**: Free (local)\n4. **local/phi-3-mini**: Free (local)\n5. **openai/gpt-4.1-nano**: $0.100/1K tokens\n6. **openai/gpt-4.1-nano-2025-04-14**: $0.100/1K tokens\n7. **openai/gpt-4o-mini-transcribe**: $0.100/1K tokens\n8. **openai/gpt-4o-mini**: $0.150/1K tokens\n

*This file shows only models you can use immediately. For complete model information, see `available_models.md`.*
