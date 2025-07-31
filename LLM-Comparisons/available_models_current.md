# Currently Available AI Models - Practical Guide

*Last updated: 2025-07-31T08:17:56.002103*

This document shows only the AI models **currently available to you** based on your API keys and installed local models.

## 🎯 Quick Summary

**Total Available Models: 82**
- 📡 **Hosted Models**: 67 (from 3 providers with API keys)
- 💻 **Local Models**: 15 (installed via Ollama)

## 🗝️ Available Providers

- **OpenAI**: ✅ Available - GPT-4o, O1, ChatGPT models\n- **Anthropic**: ✅ Available - Claude 3.5 Sonnet, Opus, Haiku\n- **xAI**: ✅ Available - Grok-2, Grok-3, Grok-4 models\n- **Google**: ❌ No API key\n
## 💻 Local Models (Ollama)

**Installed Models: 15**

- **codellama-34b**: 17.74360340554267GB ⭐⭐⭐ - Reliable general-purpose model optimized for Apple Silicon\n- **qwen2-5-coder-32b**: 18.488010296598077GB ⭐⭐⭐ - Specialized for code generation and programming tasks\n- **mixtral-8x7b**: 24.627523977309465GB ⭐⭐ - General-purpose language model\n- **deepseek-r1-32b**: 18.487999037839472GB ⭐⭐⭐ - Advanced reasoning and chain-of-thought capabilities\n- **qwen2-5-32b**: 18.488010083325207GB ⭐⭐⭐ - General-purpose language model\n- **llama3-3-70b**: 39.60022136196494GB ⭐⭐ - Reliable general-purpose model optimized for Apple Silicon\n- **qwen2-5-coder-1-5b**: 0.9183418834581971GB ⭐⭐⭐⭐⭐ - Specialized for code generation and programming tasks\n- **gemma2-9b**: 5.069330723024905GB ⭐⭐⭐⭐ - Google's safe and efficient language model\n- **qwen2-5-7b**: 4.361464951187372GB ⭐⭐⭐⭐ - General-purpose language model\n- **qwen2-5-coder-7b**: 4.361465164460242GB ⭐⭐⭐⭐ - Specialized for code generation and programming tasks\n- **deepseek-r1-8b**: 4.866510673426092GB ⭐⭐⭐⭐ - Advanced reasoning and chain-of-thought capabilities\n- **phi3-mini**: 2.0267245480790734GB ⭐⭐⭐⭐ - Microsoft's compact model with strong reasoning\n- **codellama-7b**: 3.56315696798265GB ⭐⭐⭐⭐ - Reliable general-purpose model optimized for Apple Silicon\n- **mistral-7b**: 4.072510063648224GB ⭐⭐⭐⭐ - Excellent multilingual capabilities and efficiency\n- **llama3-1-8b**: 4.582808658480644GB ⭐⭐⭐⭐ - Reliable general-purpose model optimized for Apple Silicon\n
## 📡 Hosted Models Breakdown

### Openai (51 models)\n\n**Budget Models (<$1/1K tokens):**\n- gpt-3.5-turbo: $0.500/1K tokens\n- gpt-3.5-turbo-1106: $0.500/1K tokens\n- gpt-3.5-turbo-0125: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- gpt-3.5-turbo-instruct: $1.500/1K tokens\n- gpt-3.5-turbo-instruct-0914: $1.500/1K tokens\n- gpt-4o: $5.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- gpt-4-0613: $30.000/1K tokens\n- gpt-4: $30.000/1K tokens\n- gpt-4o-realtime-preview-2025-06-03: $6.000/1K tokens\n\n### Anthropic (8 models)\n\n**Budget Models (<$1/1K tokens):**\n- claude-opus-4-20250514: $0.000/1K tokens\n- claude-sonnet-4-20250514: $0.000/1K tokens\n- claude-3-7-sonnet-20250219: $0.000/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- claude-3-5-sonnet-20241022: $3.000/1K tokens\n- claude-3-5-sonnet-20240620: $3.000/1K tokens\n\n**Premium Models (>$5/1K tokens):**\n- claude-3-opus-20240229: $15.000/1K tokens\n\n### Xai (8 models)\n\n**Budget Models (<$1/1K tokens):**\n- grok-3-mini: $1.000/1K tokens\n- grok-3-mini-fast: $0.500/1K tokens\n\n**Standard Models ($1-5/1K tokens):**\n- grok-2-1212: $2.000/1K tokens\n- grok-2-vision-1212: $2.000/1K tokens\n- grok-3: $3.000/1K tokens\n\n
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
1. **anthropic/claude-3-5-haiku-20241022**: Free (local)\n2. **anthropic/claude-3-7-sonnet-20250219**: Free (local)\n3. **anthropic/claude-opus-4-20250514**: Free (local)\n4. **anthropic/claude-sonnet-4-20250514**: Free (local)\n5. **local/codellama-34b**: Free (local)\n6. **local/codellama-7b**: Free (local)\n7. **local/deepseek-r1-32b**: Free (local)\n8. **local/deepseek-r1-8b**: Free (local)\n

*This file shows only models you can use immediately. For complete model information, see `available_models.md`.*
