# Currently Available AI Models - Practical Guide

*Last updated: 2025-07-30T15:20:47.488012*

This document shows only the AI models **currently available to you** based on your API keys and installed local models.

## 🎯 Quick Summary

**Total Available Models: 68**
- 📡 **Hosted Models**: 67 (from 3 providers with API keys)
- 💻 **Local Models**: 1 (installed via Ollama)

## 🗝️ Available Providers

- **OpenAI**: ✅ Available - GPT-4o, O1, ChatGPT models\n- **Anthropic**: ✅ Available - Claude 3.5 Sonnet, Opus, Haiku\n- **xAI**: ✅ Available - Grok-2, Grok-3, Grok-4 models\n- **Google**: ❌ No API key\n
## 💻 Local Models (Ollama)

**Installed Models: 1**

- **mistral-7b**: 4.072510063648224GB ⭐⭐⭐⭐ - Excellent multilingual capabilities and efficiency\n
## 📡 Hosted Models Breakdown

### Openai (51 models)\n\n**Budget Models (<$1/1K tokens):**\n- gpt-3.5-turbo: $0.500/1K tokens\n- gpt-3.5-turbo-1106: $0.500/1K tokens\n- gpt-3.5-turbo-0125: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- gpt-3.5-turbo-instruct: $1.500/1K tokens\n- gpt-3.5-turbo-instruct-0914: $1.500/1K tokens\n- gpt-4o: $2.500/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- gpt-4-0613: $30.000/1K tokens\n- gpt-4: $30.000/1K tokens\n- gpt-4o-realtime-preview-2025-06-03: $6.000/1K tokens\n\n### Anthropic (8 models)\n\n**Budget Models (<$1/1K tokens):**\n- claude-opus-4-20250514: $0.000/1K tokens\n- claude-sonnet-4-20250514: $0.000/1K tokens\n- claude-3-7-sonnet-20250219: $0.000/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- claude-3-5-sonnet-20241022: $3.000/1K tokens\n- claude-3-5-sonnet-20240620: $3.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- claude-3-opus-20240229: $15.000/1K tokens\n\n### Xai (8 models)\n\n**Budget Models (<$1/1K tokens):**\n- grok-3-mini: $1.000/1K tokens\n- grok-3-mini-fast: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- grok-2-1212: $2.000/1K tokens\n- grok-2-vision-1212: $2.000/1K tokens\n- grok-2-image-1212: $2.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- grok-3: $12.000/1K tokens\n- grok-3-fast: $8.000/1K tokens\n- grok-4-0709: $8.000/1K tokens\n\n
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
1. **anthropic/claude-3-5-haiku-20241022**: Free (local)\n2. **anthropic/claude-3-7-sonnet-20250219**: Free (local)\n3. **anthropic/claude-opus-4-20250514**: Free (local)\n4. **anthropic/claude-sonnet-4-20250514**: Free (local)\n5. **local/mistral-7b**: Free (local)\n6. **openai/gpt-4.1-nano**: $0.100/1K tokens\n7. **openai/gpt-4.1-nano-2025-04-14**: $0.100/1K tokens\n8. **openai/gpt-4o-mini-transcribe**: $0.100/1K tokens\n

*This file shows only models you can use immediately. For complete model information, see `available_models.md`.*
