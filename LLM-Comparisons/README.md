# Enhanced AI Model Information Collector & Intelligent Router

A comprehensive Python tool for collecting, comparing, and intelligently routing between AI models from OpenAI (ChatGPT), Anthropic (Claude), xAI (Grok), Google (Gemini), and local LLMs optimized for Apple Silicon.

## Overview

The `GetAvailableModels.py` script automatically queries multiple AI provider APIs and local installations to collect detailed information about available models, including:

- 🆔 **Model IDs and versions** (hosted and local)
- 💰 **Cost per token** (input/output pricing)
- 📏 **Context window sizes**
- 🎯 **Model strengths and capabilities**
- 📊 **Cost comparison analysis**
- 🧠 **Intelligent routing recommendations**
- 💻 **Local model specifications** (size, speed, RAM usage)

## New Features

### Enhanced Model Coverage
- **All major providers**: OpenAI, Anthropic, xAI, Google
- **Local LLMs**: Llama 3, Mistral, Mixtral, Code Llama, Phi-3, Gemma, Falcon, MPT
- **Grok-4 inclusion**: Explicitly includes Grok-4 (often omitted from other tools)
- **Apple Silicon optimization**: Optimized specifications for M2 Ultra systems
- **Tool availability detection**: Automatically detects installed local inference tools

### Interactive Sortable Tables
- **Sortable HTML table**: Click column headers to sort by context size, cost, or strengths
- **Color-coded rows**: Green (local/free), yellow (budget), red (premium)
- **Quick comparison**: Visual comparison of all 79 models in one table
- **Real-time filtering**: Easy identification of best models for specific needs

### Enhanced Local Model Support
- **Automatic detection**: Scans for installed tools (llama-cpp-python, ctransformers, transformers)
- **Local file scanning**: Finds existing model files in common cache directories
- **Loader examples**: Complete code examples for each available inference tool
- **Installation status**: Real-time status of local model availability
- **Download suggestions**: Direct links to recommended model downloads

### Intelligent Router
- **Automatic task detection**: Physics/STEM, code generation, multimodal, etc.
- **Cost-aware routing**: Select models based on budget constraints
- **Context-aware selection**: Choose models based on token requirements
- **Local preference**: Option to prefer local models for privacy/cost
- **Local-only mode**: Force local model usage with `local_only=True`
- **Fallback logic**: Graceful degradation when preferred models unavailable
- **Loader integration**: Provides complete setup code for selected local models

## Prerequisites

### API Keys (Optional)

Set environment variables for the providers you want to use:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key" 
export XAI_API_KEY="your-xai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

**Note**: Missing API keys will result in fallback to known model data - the system still works without all keys.

### Python Dependencies

```bash
pip install requests
```

### Local LLM Tools (Recommended: Ollama)

**Option 1: Ollama (Recommended)**
```bash
# Install Ollama for Apple Silicon
brew install ollama

# Start Ollama service
brew services start ollama

# Install key models
ollama pull llama3.1:8b      # Llama 3.1 8B
ollama pull mistral:7b       # Mistral 7B  
ollama pull codellama:7b     # Code Llama 7B
ollama pull phi3:mini        # Phi-3 Mini
```

**Option 2: Python Libraries (Advanced)**
```bash
pip install llama-cpp-python  # Fast CPU inference with optional GPU
pip install ctransformers     # Python API for GGUF models  
pip install transformers      # Full HuggingFace ecosystem
```

**Note**: The IntelligentLLMRouter now has native Ollama integration with automatic model detection and execution. Ollama provides the simplest setup for local models with excellent Apple Silicon performance.

## Usage

### Basic Usage

```bash
python3 GetAvailableModels.py
```

### Expected Output

The script will:
1. ✅ Check available API keys
2. 🔍 Query each provider's API for available models  
3. 💻 Check local model tool availability and scan for existing files
4. 💾 Generate `available_models.json` with structured data  
5. 📝 Generate `available_models.md` with sortable HTML table
6. 📄 Generate `available_models.html` with interactive sortable table
7. 🔄 Create current models subset files for models you can actually use
8. 🧠 Create `IntelligentLLMRouter.py` for smart model selection

### Output Files

#### `available_models.json`
Comprehensive structured data:
```json
{
  "last_updated": "2025-01-29T...",
  "providers": {
    "openai": {...},
    "anthropic": {...},
    "xai": {...},
    "google": {...}
  },
  "local_models": {
    "llama-3-8b": {
      "size_gb": 6,
      "speed_rating": 4,
      "context_window": 128000,
      "cost_per_1m_tokens": {"input": 0, "output": 0}
    }
  },
  "routing_recommendations": {...}
}
```

#### `available_models.md`
Human-readable documentation with embedded HTML table.

#### `available_models.html`
Interactive sortable table with:
- **Sortable columns**: Click headers to sort by context, cost, or strengths
- **Color-coded pricing**: Green (free/local), yellow (budget), red (premium)
- **Real-time filtering**: Quick identification of best models for specific needs
- **Browser-optimized**: Standalone HTML file for easy viewing

#### `IntelligentLLMRouter.py`
Standalone intelligent router class for automatic model selection with local support.

#### Current Models Files
Additional files showing only models currently available to you:

- **`available_models_current.json`** - JSON data for models you can actually use right now
- **`available_models_current.md`** - Documentation for your available models only  
- **`available_models_current.html`** - Interactive table of your available models

These files filter the complete model list to show only:
- Models from providers where you have API keys configured
- Local models that are actually installed via Ollama

## Model Information Collected

### Hosted Models
| Field | Description |
|-------|-------------|
| `id` | Official model identifier |
| `provider` | API provider (openai, anthropic, xai, google) |
| `pricing` | Cost per 1K tokens (input/output) |
| `context_window` | Maximum tokens in context |
| `strengths` | Key capabilities and use cases |
| `cost_per_1m_tokens` | Cost per million tokens |

### Local Models
| Field | Description |
|-------|-------------|
| `id` | Model identifier |
| `size_gb` | Model file size in GB |
| `speed_rating` | Performance rating (1-5 stars) |
| `format` | File format (GGUF, MLC, etc.) |
| `estimated_ram_usage` | RAM needed including overhead |
| `tools_available` | Available inference tools |

## Intelligent Router Usage

### Basic Routing Examples

```python
from IntelligentLLMRouter import IntelligentLLMRouter

router = IntelligentLLMRouter()

# Check available local models
local_models = router.get_available_local_models()
print(f"Available: {local_models}")  # ['llama3.1:8b', 'mistral:7b', 'codellama:7b', 'phi3:mini']

# Automatic routing for hosted models
result = router.route_request("Explain quantum mechanics")
print(f"Recommended: {result['recommended_model']}")  # grok-4
print(f"Execution: {result['execution_info']['execution_type']}")  # api

# Prefer local models
result = router.route_request(
    "Write a Python function",
    prefer_local=True
)
print(f"Recommended: {result['recommended_model']}")  # code-llama-7b
print(f"Ollama Model: {result['execution_info']['ollama_model']}")  # codellama:7b
print(f"Command: {result['execution_info']['command']}")  # ollama run codellama:7b
```

### Direct Local Model Queries

```python
# Query local models directly via Ollama
response = router.query_ollama('mistral-7b', 'Hello! Introduce yourself.')
print(response)  # Direct response from local Mistral model

# Handle errors gracefully
try:
    response = router.query_ollama('nonexistent-model', 'Hello')
except ValueError as e:
    print(f"Error: {e}")  # Model not installed
```

### Advanced Routing with Constraints

```python
# Cost-conscious routing with local preference
result = router.route_request(
    "Analyze this complex data",
    max_cost_per_1k=2.0,
    prefer_local=True,
    context_length_estimate=50000
)

# Check execution details
if result['execution_info']['execution_type'] == 'ollama':
    print(f"✅ Using local model: {result['execution_info']['ollama_model']}")
    print(f"📱 Available: {result['execution_info']['available']}")
    
    # Execute query if available
    if result['execution_info']['available']:
        response = router.query_ollama(result['recommended_model'], "Your prompt here")
        print(f"Response: {response[:100]}...")
else:
    print(f"🌐 Using hosted model via {result['execution_info']['provider']}")
```

## Task-Based Routing Logic

### Automatic Task Detection
- **Physics/STEM**: Keywords like "physics", "thermodynamics", "quantum"
- **Code Generation**: Keywords like "function", "class", "def", "import"
- **Multimodal**: Keywords like "image", "photo", "diagram", "visual"
- **Long Context**: Prompts > 10,000 characters
- **Fast/Simple**: Short prompts with question words

### Routing Recommendations
| Task Type | Primary | Fallback | Local Option | Reasoning |
|-----------|---------|----------|--------------|-----------|
| Physics/STEM | Grok-4 | Claude 3 Opus | Mixtral 8x7B | STEM-focused models |
| Code Generation | GPT-4o | Claude 3.5 Sonnet | Code Llama 7B | Tool use & coding |
| Long Context | Gemini 2.5 Pro | Claude 3 Opus | Llama 3 8B | Large context windows |
| Cost-Sensitive | Claude 3 Haiku | GPT-3.5 Turbo | Phi-3 Mini | Cheapest options |
| Multimodal | GPT-4o | Gemini Pro Vision | - | Vision capabilities |

## Local Model Specifications

### Best for Different Use Cases
- **Balanced Performance**: Llama 3 8B (6GB, ⭐⭐⭐⭐)
- **Fastest Local**: Mistral 7B (6GB, ⭐⭐⭐⭐⭐)
- **Best Reasoning**: Mixtral 8x7B (20GB, ⭐⭐)
- **Code Specialist**: Code Llama 7B (8GB, ⭐⭐⭐⭐)
- **Most Efficient**: Phi-3 Mini (3GB, ⭐⭐⭐⭐⭐)

### Apple Silicon Optimization
All local models include:
- Optimized GGUF quantization recommendations
- RAM usage estimates with overhead
- Speed ratings based on M2 Ultra performance
- Format recommendations (GGUF preferred)

## Provider-Specific Features

### OpenAI
- Real-time API data from `/v1/models`
- Includes latest O1 reasoning models
- Multimodal GPT-4o support

### Anthropic (Claude)
- Claude 3.5 Sonnet (latest) prioritized
- Large 200K context windows
- Excellent coding capabilities

### xAI (Grok)
- **Grok-4 explicitly included** (often missing from other tools)
- STEM and physics emphasis
- Real-time information access

### Google (Gemini)
- Ultra-long context support (1M+ tokens)
- Multimodal capabilities
- Grounded responses

### Local Models (via Ollama)
- **Privacy-preserving inference** - Data never leaves your machine
- **No API costs** - Only compute/electricity costs
- **Offline capability** - Works without internet connection
- **Apple Silicon Metal acceleration** - Optimized for M1/M2/M3 chips
- **Simple management** - `ollama pull model:tag` to install
- **Automatic detection** - Router finds available models automatically
- **Direct integration** - Native Ollama API calls via subprocess

## Important: PDF Processing Capabilities

**⚠️ PDF Processing Reality Check:**

🌐 **Web Apps (Outstanding capability):**
- ChatGPT web interface, Claude web interface, etc.
- Have integrated PDF processing tools
- Can directly upload and analyze PDF files

🐍 **Python APIs (Limited capability):**
- OpenAI Python API, Anthropic Python API, etc.
- **Cannot** directly process PDF files
- Require external PDF → text conversion

💻 **Local LLMs (Same as Python APIs - Limited capability):**
- Ollama models, llama-cpp, transformers, etc.
- **Cannot** directly process PDF files
- Require external PDF → text conversion

**The key insight:** Local LLMs have the **same PDF limitations as Python APIs**, not the enhanced capabilities of web apps.

### PDF Processing Workflow for Python APIs & Local LLMs:

```python
# Required for both Python APIs and Local LLMs
import PyPDF2  # or pdfplumber, pymupdf, etc.

# 1. Extract text from PDF
with open('document.pdf', 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

# 2. Send to model (works same for hosted APIs or local LLMs)
# For local LLM via Ollama:
response = subprocess.run(['ollama', 'run', 'llama3.1:8b', f"Analyze: {text}"])

# For hosted API:
response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": f"Analyze: {text}"}])
```

This system correctly identifies all models as having `"pdf_processing": false` because it focuses on Python API and local capabilities, not web app features.

## Updating Information

Run periodically to keep current:

```bash
# Weekly/monthly updates recommended
python3 GetAvailableModels.py
```

Updates capture:
- New model releases
- Pricing changes  
- Local tool availability
- Routing logic improvements

## Cost Analysis Features

### Cost Comparison
- Per-token and per-million-token pricing
- Local models show $0.00 API cost
- Sort by cost efficiency
- Budget-based filtering

### Example Cost Tiers
- **Free**: Local models only
- **Budget**: <$1.00/1K tokens (Claude Haiku, GPT-3.5)
- **Standard**: <$5.00/1K tokens (Claude Sonnet, GPT-4o-mini)
- **Premium**: Unlimited (GPT-4o, Claude Opus, Grok-4)

## Advanced Features

### Constraint-Based Selection
```python
result = router.route_request(
    prompt="Complex physics problem",
    max_cost_per_1k=3.0,           # Budget constraint
    prefer_local=True,              # Privacy preference
    require_multimodal=False,       # No vision needed
    context_length_estimate=50000   # Long context
)
```

### Local Model Management with Ollama

```python
# Check which local models are available via Ollama
available = router.get_available_local_models()
print(f"Installed models: {available}")

# Check if specific model is available
if router._check_ollama_model_available('mistral:7b'):
    print("✅ Mistral 7B is ready for use")
else:
    print("❌ Run: ollama pull mistral:7b")

# Batch query multiple models
models_to_test = ['llama3.1:8b', 'mistral:7b', 'codellama:7b']
prompt = "Write a hello world function in Python"

for model in models_to_test:
    if router._check_ollama_model_available(model):
        response = router.query_ollama(model.replace(':', '-'), prompt)
        print(f"{model}: {response[:50]}...")
```

### Command Line Testing

```bash
# Test the router directly
python3 IntelligentLLMRouter.py

# Expected output shows:
# 🔍 Available Local Models via Ollama:
#   ✅ phi3:mini
#   ✅ codellama:7b  
#   ✅ mistral:7b
#   ✅ llama3.1:8b
# 
# 🧠 Intelligent LLM Router - Test Results
# [Routing examples with actual Ollama queries]
```

### Fallback Logic
1. Check preferred model against constraints
2. Try fallback options in order
3. Apply cost and context filters
4. Default to most available option
5. Provide local alternatives when API models unavailable

### Tool Detection & Management
- Automatic detection of installed inference tools
- Graceful handling of missing dependencies
- Installation suggestions for local models
- File system scanning for existing models

### Extensibility
- Easy to add new providers
- Configurable routing rules
- Plugin architecture for local tools
- Custom constraint functions
- Automatic tool availability mapping

## Troubleshooting

### Common Issues

1. **No API Keys**
   ```
   ⚠️ Missing API keys: OPENAI_API_KEY (will use fallback data)
   ```
   Solution: System works with fallback data, but API keys provide real-time info

2. **Local Tools Not Found**
   ```
   🔍 Checking local models...
   ✅ Found 10 local model configurations
   🔧 Tools available: ctransformers, transformers
   ❌ Not available: llama-cpp-python
   ```
   Solution: Install tools with `pip install llama-cpp-python` or use available alternatives

3. **Router File Not Found**
   ```python
   router = IntelligentLLMRouter('available_models.json')
   # Warning: available_models.json not found. Using default configuration.
   ```
   Solution: Run `GetAvailableModels.py` first to generate data file

## Contributing

### Adding New Providers
1. Add API key environment variable
2. Implement `get_[provider]_models()` method
3. Add pricing and capability information
4. Update routing recommendations

### Adding Local Models
1. Add model specs to `local_model_specs`
2. Update pricing info (typically $0.00)
3. Add context window information
4. Include strengths description

## License

This tool is provided as-is for educational and development purposes. Ensure compliance with each provider's API terms of service.

## Key Advantages

- **Grok-4 included** (often omitted elsewhere)
- **Interactive sortable tables** for easy model comparison
- **Local model support** with Apple Silicon optimization and auto-detection
- **Intelligent routing** based on task analysis
- **Cost optimization** with local alternatives
- **Graceful fallbacks** when APIs unavailable
- **Privacy options** with local inference
- **Tool integration** with complete loader examples
- **Real-time data** where APIs support it
- **Comprehensive documentation** in multiple formats``