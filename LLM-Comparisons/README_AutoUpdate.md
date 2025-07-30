# Auto-Update System for LLM Models

## Overview

The AutoUpdateSystem automatically detects new models (like gpt-5, claude-4, grok-5) and installs local LLMs via Ollama. It integrates with the existing model comparison system to keep everything up-to-date.

## Features

✅ **Automatic Model Detection**
- Monitors OpenAI, Anthropic, xAI, and Google APIs for new models
- Detects next-generation models like gpt-5, claude-4, grok-5
- Updates model database with real-time pricing

✅ **Auto-Installation of Local LLMs** 
- Automatically installs new Ollama models
- Optimized for Apple Silicon (prefers 7b-13b models)
- Configurable model limits and size preferences
- Disk space checking before installation

✅ **Smart Scheduling**
- Configurable update intervals (default: 24 hours)
- Background monitoring with minimal system impact
- Update history logging and error tracking

✅ **Integration**
- Works with existing GetAvailableModels.py system
- Auto-opens updated comparison tables in browser
- Updates IntelligentLLMRouter with new models

## Usage

### Quick Start
```bash
# Check system status
python3 AutoUpdateSystem.py status

# Run immediate update check
python3 AutoUpdateSystem.py check

# Start continuous monitoring (runs every 24 hours)
python3 AutoUpdateSystem.py schedule
```

### Configuration
```bash
# Enable/disable auto-installation
python3 AutoUpdateSystem.py config auto_install_local_models true

# Set maximum local models (default: 10)
python3 AutoUpdateSystem.py config max_local_models 15

# Change update interval to 12 hours
python3 AutoUpdateSystem.py config check_interval_hours 12
```

### Manual Control
```python
from AutoUpdateSystem import AutoUpdateSystem

# Initialize system
updater = AutoUpdateSystem()

# Force update check
updater.force_update_check()

# Check what new models are available
new_models = updater.check_for_new_models()
print(f"New hosted models: {new_models['hosted']}")
print(f"New local models: {new_models['local']}")

# Get system status
status = updater.get_update_status()
```

## Configuration Options

The system creates `auto_update_config.json` with these settings:

```json
{
  "auto_update_enabled": true,
  "check_interval_hours": 24,
  "auto_install_local_models": true,
  "max_local_models": 10,
  "preferred_model_sizes": ["7b", "8b", "13b"],
  "exclude_patterns": ["*:latest"]
}
```

### Key Settings
- **auto_update_enabled**: Master switch for all automatic updates
- **check_interval_hours**: How often to check for new models
- **auto_install_local_models**: Whether to auto-install Ollama models
- **max_local_models**: Maximum number of local models to keep installed
- **preferred_model_sizes**: Model sizes to prefer for Apple Silicon
- **exclude_patterns**: Model patterns to avoid installing

## Recommended Local Models

The system automatically considers these models for installation:

**Core Models:**
- llama3.1:8b, llama3.2:3b - Meta's latest models
- mistral:7b, mixtral:8x7b - Mistral AI models
- codellama:7b, codellama:13b - Code-specialized models
- phi3:mini, phi3:medium - Microsoft's efficient models

**Specialized Models:**
- qwen2.5:7b, qwen2.5:14b - Alibaba's multilingual models
- deepseek-coder:6.7b - Advanced coding model
- gemma2:9b - Google's open model
- neural-chat:7b - Conversational model

## Apple Silicon Optimization

The system is optimized for Apple Silicon Macs:
- Prefers smaller models (7b-13b parameters) for better performance
- Checks available disk space before installation
- Respects memory constraints with model limits
- Fast installation with parallel processing

## Important: PDF Processing Capabilities

**Local LLMs have the SAME PDF limitations as Python APIs:**

🚫 **Cannot directly process PDF files**
- Local LLMs (Ollama) are text-only models
- Same limitations as Python APIs for hosted models
- Require external PDF → text conversion

🌐 **Web apps vs APIs/Local models:**
- **Web apps**: Have integrated PDF processing tools (Outstanding capability)
- **Python APIs**: Limited - require external PDF parsing (Limited capability)  
- **Local LLMs**: Same as Python APIs - require external PDF parsing (Limited capability)

💡 **For PDF processing with local LLMs:**
```python
# Required approach for both Python APIs and Local LLMs
import PyPDF2  # or pdfplumber, pymupdf, etc.

# 1. Extract text from PDF
with open('document.pdf', 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

# 2. Send extracted text to local LLM
ollama run llama3.1:8b "Analyze this text: " + text
```

## Integration with Existing System

### Auto-Opening Results
When new models are detected and the database is updated, the system automatically:
1. Runs GetAvailableModels.py to collect latest data
2. Generates updated HTML comparison table
3. Auto-opens the results in your default browser

### IntelligentLLMRouter Integration
New models are automatically available in the router for:
- Task-based model selection
- Cost-optimized routing
- Local vs hosted model preferences

## Monitoring and Logs

### Update History
All updates are logged in `model_update_log.json`:
```json
[
  {
    "timestamp": "2025-01-15T10:30:00",
    "action": "install_local_model", 
    "model": "llama3.2:3b",
    "success": true,
    "install_time_seconds": 45.2
  }
]
```

### Status Monitoring
Check system health with:
```bash
python3 AutoUpdateSystem.py status
```

## Scheduling for Production

### macOS Launchd (Recommended)
Create `~/Library/LaunchAgents/com.llm.autoupdate.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llm.autoupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/AutoUpdateSystem.py</string>
        <string>check</string>
    </array>
    <key>StartInterval</key>
    <integer>86400</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Cron Alternative
```bash
# Edit crontab
crontab -e

# Add daily check at 2 AM
0 2 * * * cd /Users/davidlary/Dropbox/Environments/Code/Pedegree/LLM-Comparisons && python3 AutoUpdateSystem.py check
```

## Troubleshooting

### Common Issues

**"No module named 'schedule'"**
```bash
pip3 install schedule
```

**"Ollama not found"**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

**Disk space warnings**
- Check available space: `df -h`
- Remove old models: `ollama rm <model-name>`
- Adjust max_local_models setting

**API rate limits**
- The system respects API rate limits
- Failed checks are logged and retried on next cycle
- Consider increasing check_interval_hours if needed

### Debug Mode
For detailed logging, modify the script to set debug=True or run with verbose output.

## Future Enhancements

Planned features:
- Email notifications for new model releases
- Slack/Discord webhook integrations  
- Model performance benchmarking
- Automatic A/B testing of new models
- Cost tracking and optimization alerts

## Support

- Check logs in `model_update_log.json`
- Review configuration in `auto_update_config.json`  
- Monitor system status with `python3 AutoUpdateSystem.py status`
- For issues, check the troubleshooting section above