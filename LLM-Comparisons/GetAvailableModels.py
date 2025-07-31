#!/usr/bin/env python3
"""
GetAvailableModels.py - Comprehensive AI Model Information Collector & Intelligent Router

This script queries APIs and local installations for OpenAI (ChatGPT), Anthropic (Claude), 
xAI (Grok), Google (Gemini), and local LLMs to collect comprehensive information including:
- Model IDs and versions
- Cost per token (input/output) 
- Context window sizes
- Model strengths and capabilities
- Local vs hosted availability
- Intelligent routing recommendations

Outputs both markdown and JSON formats for easy consumption by agent systems.
Includes an intelligent router for optimal model selection based on task requirements.
"""

import os
import json
import requests
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys
import re
import time
from urllib.parse import urlparse, urljoin

class EnhancedModelInfoCollector:
    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.xai_api_key = os.getenv('XAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Dynamic discovery endpoints
        self.api_endpoints = {
            'openai': 'https://api.openai.com/v1/models',
            'anthropic': 'https://api.anthropic.com/v1/models',
            'xai': 'https://api.x.ai/v1/models',
            'google': 'https://generativelanguage.googleapis.com/v1/models',
            'ollama': 'http://localhost:11434/api/tags'
        }
        
        # Model release dates for non-OpenAI models (OpenAI provides 'created' field)
        self.model_release_dates = {
            'anthropic': {
                'claude-3-5-sonnet-20241022': '2024-10-22',
                'claude-3-5-sonnet-20240620': '2024-06-20',
                'claude-3-opus-20240229': '2024-02-29',
                'claude-3-sonnet-20240229': '2024-02-29',
                'claude-3-haiku-20240307': '2024-03-07',
            },
            'xai': {
                'grok-2-1212': '2024-12-12',
                'grok-2-vision-1212': '2024-12-12',
                'grok-2-image-1212': '2024-12-12',
                'grok-3': '2025-01-15',
                'grok-3-fast': '2025-01-15',
                'grok-3-mini': '2025-01-15',
                'grok-3-mini-fast': '2025-01-15',
                'grok-4': '2024-07-09',
                'grok-4-0709': '2024-07-09',
            },
            'google': {
                'gemini-2.5-pro': '2024-12-11',
                'gemini-2.5-flash': '2024-12-11',
                'gemini-pro': '2023-12-06',
                'gemini-pro-vision': '2023-12-06',
            },
            'local': {
                # Latest 2025 models
                'llama-3.3-70b': '2024-12-06',
                'deepseek-r1-8b': '2025-01-20',
                'deepseek-r1-7b': '2025-01-20',
                'qwen3-8b': '2025-01-13',
                'qwen3-14b': '2025-01-13',
                'qwen3-32b': '2025-01-13',
                'qwen2.5-coder-7b': '2024-11-11',
                'qwen2.5-coder-14b': '2024-11-11',
                'qwen2.5-coder-32b': '2024-11-11',
                'qwen2.5-vl-7b': '2024-12-28',
                'qwen2.5-vl-32b': '2024-12-28',
                'llava-13b': '2024-07-15',
                'qwq-32b': '2024-11-27',
                'llama-3.1-8b': '2024-07-23',
                'llama-3.1-70b': '2024-07-23',
                'gemma3-9b': '2024-12-11',
                'phi4-14b': '2024-12-11',
                'qwen3-1.7b': '2025-01-13',
                'gemma3-4b': '2024-12-11',
                'mistral-nemo-12b': '2024-07-18'
            }
        }
        
        self.models_data = {
            'last_updated': datetime.now().isoformat(),
            'providers': {},
            'local_models': {},
            'routing_recommendations': {}
        }
        
        # Enhanced model strengths including local models
        self.model_strengths = {
            'openai': {
                'gpt-4o': 'Latest multimodal model, excellent for complex reasoning, vision, and tool use',
                'gpt-4o-mini': 'Cost-effective version of GPT-4o, good balance of capability and price',
                'gpt-4-turbo': 'Advanced reasoning, large context window, supports tools and vision',
                'gpt-4': 'Strong reasoning and creative tasks, reliable for complex problems',
                'gpt-3.5-turbo': 'Fast and cost-effective for simpler tasks and conversations',
                'o1-preview': 'Advanced reasoning model, excellent for complex problem-solving',
                'o1-mini': 'Reasoning-focused model optimized for coding and math tasks'
            },
            'anthropic': {
                'claude-3-5-sonnet-20241022': 'Latest Claude, excellent coding and analysis capabilities',
                'claude-3-5-sonnet-20240620': 'Previous Claude 3.5, strong general purpose model',  
                'claude-3-opus-20240229': 'Most capable Claude model for complex reasoning tasks',
                'claude-3-sonnet-20240229': 'Balanced performance and speed for most tasks',
                'claude-3-haiku-20240307': 'Fastest Claude model, good for simple tasks and high volume'
            },
            'xai': {
                'grok-beta': 'Real-time information access, good for current events and factual queries',
                'grok-vision-beta': 'Multimodal Grok with vision capabilities',
                'grok-4': 'STEM and science focused, Musk\'s physics emphasis, strong reasoning'
            },
            'google': {
                'gemini-2.5-pro': 'Long context up to 1M+ tokens, multimodal, grounded responses',
                'gemini-2.5-flash': 'Fast version of Gemini 2.5, optimized for speed',
                'gemini-pro': 'General purpose model with strong capabilities',
                'gemini-pro-vision': 'Multimodal version with vision capabilities'
            },
            'local': {
                # Latest 2025 Flagship Models
                'llama-3.3-70b': 'GPT-4 class performance, excellent reasoning and instruction following',
                'deepseek-r1-8b': 'Advanced reasoning model, competitive with O1-mini, chain-of-thought',
                'deepseek-r1-7b': 'Efficient reasoning model with strong problem-solving capabilities',
                'qwen3-8b': 'Latest Qwen generation, excellent multilingual and general capabilities',
                'qwen3-14b': 'Larger Qwen3 model with enhanced reasoning and coding abilities',
                'qwen3-32b': 'High-performance Qwen3 model for complex tasks and reasoning',
                
                # Specialized Coding Models
                'qwen2.5-coder-7b': 'State-of-the-art code generation, competitive with GPT-4 for coding',
                'qwen2.5-coder-14b': 'Enhanced coding model with superior debugging and refactoring',
                'qwen2.5-coder-32b': 'Premium coding assistant, handles complex codebases and architecture',
                
                # Vision-Language Models
                'qwen2.5-vl-7b': 'Multimodal model with vision understanding and reasoning',
                'qwen2.5-vl-32b': 'Advanced vision-language model with tool use capabilities',
                'llava-13b': 'Open-source vision model, good for image analysis and description',
                
                # Reasoning Specialist
                'qwq-32b': 'Specialized reasoning model with enhanced logical thinking',
                
                # Proven General Models
                'llama-3.1-8b': 'Reliable general purpose model, well-optimized for Apple Silicon',
                'llama-3.1-70b': 'High-performance Llama model for complex reasoning tasks',
                'gemma3-9b': 'Latest Gemma with improved safety and multilingual support',
                'phi4-14b': 'Microsoft\'s latest small language model with strong reasoning',
                
                # Efficient Options
                'qwen3-1.7b': 'Ultra-lightweight model for basic tasks and edge deployment',
                'gemma3-4b': 'Compact model with good performance-to-size ratio',
                'mistral-nemo-12b': 'Balanced model with strong multilingual capabilities'
            }
        }
        
        # Enhanced pricing information including local models (local = 0 cost)
        self.pricing_info = {
            'openai': {
                # Current models with corrected 2025 pricing
                'gpt-4o': {'input': 5.0, 'output': 20.0},
                'gpt-4o-mini': {'input': 0.15, 'output': 0.6},
                'gpt-4-turbo': {'input': 10.0, 'output': 30.0},
                'gpt-4': {'input': 30.0, 'output': 60.0},
                'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5},
                'o1-preview': {'input': 15.0, 'output': 60.0},
                'o1-mini': {'input': 3.0, 'output': 12.0},
                'o1': {'input': 15.0, 'output': 60.0},
                # Legacy/versioned models - same pricing as current versions
                'gpt-4-0613': {'input': 30.0, 'output': 60.0},
                'gpt-4-1106-preview': {'input': 10.0, 'output': 30.0},
                'gpt-4-0125-preview': {'input': 10.0, 'output': 30.0},
                'gpt-4-turbo-preview': {'input': 10.0, 'output': 30.0},
                'gpt-4-turbo-2024-04-09': {'input': 10.0, 'output': 30.0},
                'gpt-4o-2024-05-13': {'input': 5.0, 'output': 20.0},
                'gpt-4o-2024-08-06': {'input': 5.0, 'output': 20.0},
                'gpt-4o-2024-11-20': {'input': 5.0, 'output': 20.0},
                'gpt-4o-mini-2024-07-18': {'input': 0.15, 'output': 0.6},
                'gpt-3.5-turbo-0125': {'input': 0.5, 'output': 1.5},
                'gpt-3.5-turbo-1106': {'input': 0.5, 'output': 1.5},
                'gpt-3.5-turbo-instruct': {'input': 1.5, 'output': 2.0},
                'gpt-3.5-turbo-instruct-0914': {'input': 1.5, 'output': 2.0},
                'gpt-3.5-turbo-16k': {'input': 3.0, 'output': 4.0},
                'o1-mini-2024-09-12': {'input': 3.0, 'output': 12.0},
                'o1-2024-12-17': {'input': 15.0, 'output': 60.0},
                'o1-pro': {'input': 0.15, 'output': 0.60},
                'o1-pro-2025-03-19': {'input': 0.15, 'output': 0.60},
                'chatgpt-4o-latest': {'input': 5.0, 'output': 20.0},
                # Realtime/Audio models (estimated pricing)
                'gpt-4o-realtime-preview': {'input': 6.0, 'output': 24.0},
                'gpt-4o-realtime-preview-2024-10-01': {'input': 6.0, 'output': 24.0},
                'gpt-4o-realtime-preview-2024-12-17': {'input': 6.0, 'output': 24.0},
                'gpt-4o-realtime-preview-2025-06-03': {'input': 6.0, 'output': 24.0},
                'gpt-4o-audio-preview': {'input': 6.0, 'output': 24.0},
                'gpt-4o-audio-preview-2024-10-01': {'input': 6.0, 'output': 24.0},
                'gpt-4o-audio-preview-2024-12-17': {'input': 6.0, 'output': 24.0},
                'gpt-4o-audio-preview-2025-06-03': {'input': 6.0, 'output': 24.0},
                'gpt-4o-mini-realtime-preview': {'input': 0.6, 'output': 2.4},
                'gpt-4o-mini-realtime-preview-2024-12-17': {'input': 0.6, 'output': 2.4},
                'gpt-4o-mini-audio-preview': {'input': 0.6, 'output': 2.4},
                'gpt-4o-mini-audio-preview-2024-12-17': {'input': 0.6, 'output': 2.4},
                # Newer models (estimated based on capabilities)
                'gpt-4.1': {'input': 15.0, 'output': 45.0},
                'gpt-4.1-2025-04-14': {'input': 15.0, 'output': 45.0},
                'gpt-4.1-mini': {'input': 0.3, 'output': 1.2},
                'gpt-4.1-mini-2025-04-14': {'input': 0.3, 'output': 1.2},
                'gpt-4.1-nano': {'input': 0.1, 'output': 0.4},
                'gpt-4.1-nano-2025-04-14': {'input': 0.1, 'output': 0.4},
                # Search and specialized models
                'gpt-4o-search-preview': {'input': 3.0, 'output': 12.0},
                'gpt-4o-search-preview-2025-03-11': {'input': 3.0, 'output': 12.0},
                'gpt-4o-mini-search-preview': {'input': 0.2, 'output': 0.8},
                'gpt-4o-mini-search-preview-2025-03-11': {'input': 0.2, 'output': 0.8},
                'gpt-4o-transcribe': {'input': 2.0, 'output': 8.0},
                'gpt-4o-mini-transcribe': {'input': 0.1, 'output': 0.4},
                'gpt-4o-mini-tts': {'input': 0.15, 'output': 0.6}
            },
            'anthropic': {
                'claude-3-5-sonnet-20241022': {'input': 3.0, 'output': 15.0},
                'claude-3-5-sonnet-20240620': {'input': 3.0, 'output': 15.0},
                'claude-3-opus-20240229': {'input': 15.0, 'output': 75.0},
                'claude-3-sonnet-20240229': {'input': 3.0, 'output': 15.0},
                'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25}
            },
            'xai': {
                'grok-beta': {'input': 5.0, 'output': 15.0},
                'grok-vision-beta': {'input': 5.0, 'output': 15.0},
                'grok-4': {'input': 3.0, 'output': 15.0},
                'grok-4-0709': {'input': 3.0, 'output': 15.0},
                'grok-2-1212': {'input': 2.0, 'output': 10.0},
                'grok-2-vision-1212': {'input': 2.0, 'output': 10.0},
                'grok-2-image-1212': {'input': 2.0, 'output': 10.0},
                'grok-3': {'input': 3.0, 'output': 15.0},
                'grok-3-fast': {'input': 3.0, 'output': 15.0},
                'grok-3-mini': {'input': 1.0, 'output': 4.0},
                'grok-3-mini-fast': {'input': 0.5, 'output': 2.0}
            },
            'google': {
                'gemini-2.5-pro': {'input': 4.0, 'output': 20.0},
                'gemini-2.5-flash': {'input': 1.0, 'output': 5.0},
                'gemini-pro': {'input': 1.0, 'output': 3.0},
                'gemini-pro-vision': {'input': 1.5, 'output': 4.0}
            },
            'local': {
                # Local models have no API costs, only compute/electricity
                'llama-3.3-70b': {'input': 0.0, 'output': 0.0},
                'deepseek-r1-8b': {'input': 0.0, 'output': 0.0},
                'deepseek-r1-7b': {'input': 0.0, 'output': 0.0},
                'qwen3-8b': {'input': 0.0, 'output': 0.0},
                'qwen3-14b': {'input': 0.0, 'output': 0.0},
                'qwen3-32b': {'input': 0.0, 'output': 0.0},
                'qwen2.5-coder-7b': {'input': 0.0, 'output': 0.0},
                'qwen2.5-coder-14b': {'input': 0.0, 'output': 0.0},
                'qwen2.5-coder-32b': {'input': 0.0, 'output': 0.0},
                'qwen2.5-vl-7b': {'input': 0.0, 'output': 0.0},
                'qwen2.5-vl-32b': {'input': 0.0, 'output': 0.0},
                'llava-13b': {'input': 0.0, 'output': 0.0},
                'qwq-32b': {'input': 0.0, 'output': 0.0},
                'llama-3.1-8b': {'input': 0.0, 'output': 0.0},
                'llama-3.1-70b': {'input': 0.0, 'output': 0.0},
                'gemma3-9b': {'input': 0.0, 'output': 0.0},
                'phi4-14b': {'input': 0.0, 'output': 0.0},
                'qwen3-1.7b': {'input': 0.0, 'output': 0.0},
                'gemma3-4b': {'input': 0.0, 'output': 0.0},
                'mistral-nemo-12b': {'input': 0.0, 'output': 0.0}
            }
        }
        
        # Enhanced context window sizes
        self.context_windows = {
            'openai': {
                # GPT-4o series
                'gpt-4o': 128000,
                'gpt-4o-2024-05-13': 128000,
                'gpt-4o-2024-08-06': 128000,
                'gpt-4o-2024-11-20': 128000,
                'chatgpt-4o-latest': 128000,
                'gpt-4o-mini': 128000,
                'gpt-4o-mini-2024-07-18': 128000,
                'gpt-4o-mini-tts': 128000,
                
                # GPT-4o Audio/Realtime models
                'gpt-4o-realtime-preview': 128000,
                'gpt-4o-realtime-preview-2024-10-01': 128000,
                'gpt-4o-realtime-preview-2024-12-17': 128000,
                'gpt-4o-realtime-preview-2025-06-03': 128000,
                'gpt-4o-audio-preview': 128000,
                'gpt-4o-audio-preview-2024-10-01': 128000,
                'gpt-4o-audio-preview-2024-12-17': 128000,
                'gpt-4o-audio-preview-2025-06-03': 128000,
                'gpt-4o-mini-realtime-preview': 128000,
                'gpt-4o-mini-realtime-preview-2024-12-17': 128000,
                'gpt-4o-mini-audio-preview': 128000,
                'gpt-4o-mini-audio-preview-2024-12-17': 128000,
                
                # GPT-4o Search and specialized models
                'gpt-4o-search-preview': 128000,
                'gpt-4o-search-preview-2025-03-11': 128000,
                'gpt-4o-mini-search-preview': 128000,
                'gpt-4o-mini-search-preview-2025-03-11': 128000,
                'gpt-4o-transcribe': 128000,
                'gpt-4o-mini-transcribe': 128000,
                
                # GPT-4 series
                'gpt-4': 8192,
                'gpt-4-0613': 8192,
                'gpt-4-turbo': 128000,
                'gpt-4-turbo-preview': 128000,
                'gpt-4-turbo-2024-04-09': 128000,
                'gpt-4-1106-preview': 128000,
                'gpt-4-0125-preview': 128000,
                
                # GPT-4.1 series
                'gpt-4.1': 128000,
                'gpt-4.1-2025-04-14': 128000,
                'gpt-4.1-mini': 128000,
                'gpt-4.1-mini-2025-04-14': 128000,
                'gpt-4.1-nano': 128000,
                'gpt-4.1-nano-2025-04-14': 128000,
                
                # GPT-3.5 series
                'gpt-3.5-turbo': 16385,
                'gpt-3.5-turbo-1106': 16385,
                'gpt-3.5-turbo-0125': 16385,
                'gpt-3.5-turbo-instruct': 4096,
                'gpt-3.5-turbo-instruct-0914': 4096,
                'gpt-3.5-turbo-16k': 16384,
                
                # o1 series
                'o1': 200000,
                'o1-2024-12-17': 200000,
                'o1-mini': 128000,
                'o1-mini-2024-09-12': 128000,
                'o1-pro': 200000,
                'o1-pro-2025-03-19': 200000,
                'o1-preview': 128000
            },
            'anthropic': {
                'claude-3-5-sonnet-20241022': 200000,
                'claude-3-5-sonnet-20240620': 200000,
                'claude-3-opus-20240229': 200000,
                'claude-3-sonnet-20240229': 200000,
                'claude-3-haiku-20240307': 200000
            },
            'xai': {
                'grok-beta': 131072,
                'grok-vision-beta': 131072,
                'grok-4': 128000,
                'grok-4-0709': 128000,
                'grok-2-1212': 128000,
                'grok-2-vision-1212': 128000,
                'grok-2-image-1212': 128000,
                'grok-3': 128000,
                'grok-3-fast': 128000,
                'grok-3-mini': 128000,
                'grok-3-mini-fast': 128000
            },
            'google': {
                'gemini-2.5-pro': 1000000,  # Up to 1M+ tokens
                'gemini-2.5-flash': 1000000,
                'gemini-pro': 128000,
                'gemini-pro-vision': 128000
            },
            'local': {
                # Latest 2025 models with enhanced context windows
                'llama-3.3-70b': 131072,  # 128K context window
                'deepseek-r1-8b': 65536,   # 64K context window  
                'deepseek-r1-7b': 65536,   # 64K context window
                'qwen3-8b': 131072,        # 128K context window
                'qwen3-14b': 131072,       # 128K context window
                'qwen3-32b': 131072,       # 128K context window
                'qwen2.5-coder-7b': 131072,  # 128K context window
                'qwen2.5-coder-14b': 131072, # 128K context window
                'qwen2.5-coder-32b': 131072, # 128K context window
                'qwen2.5-vl-7b': 65536,   # 64K context window for vision
                'qwen2.5-vl-32b': 65536,  # 64K context window for vision
                'llava-13b': 32768,       # 32K context window
                'qwq-32b': 131072,        # 128K context window for reasoning
                'llama-3.1-8b': 131072,   # 128K context window
                'llama-3.1-70b': 131072,  # 128K context window
                'gemma3-9b': 131072,      # 128K context window
                'phi4-14b': 131072,       # 128K context window
                'qwen3-1.7b': 131072,     # 128K context window
                'gemma3-4b': 131072,      # 128K context window
                'mistral-nemo-12b': 131072 # 128K context window
            }
        }
        
        # Local model specifications
        self.local_model_specs = {
            # Latest 2025 Models - Top Tier
            'llama-3.3-70b': {'size_gb': 43, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'llama3.3:70b'},
            'deepseek-r1-8b': {'size_gb': 5, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'deepseek-r1:8b'},
            'deepseek-r1-7b': {'size_gb': 4.7, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'deepseek-r1:7b'},
            'qwen3-8b': {'size_gb': 5.2, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen3:8b'},
            'qwen3-14b': {'size_gb': 9.0, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen3:14b'},
            'qwen3-32b': {'size_gb': 20, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen3:32b'},
            
            # Latest Coding Models
            'qwen2.5-coder-7b': {'size_gb': 4.7, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen2.5-coder:7b'},
            'qwen2.5-coder-14b': {'size_gb': 9.0, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen2.5-coder:14b'},
            'qwen2.5-coder-32b': {'size_gb': 20, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen2.5-coder:32b'},
            
            # Vision Models
            'qwen2.5-vl-7b': {'size_gb': 6.0, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen2.5vl:7b'},
            'qwen2.5-vl-32b': {'size_gb': 21, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen2.5vl:32b'},
            'llava-13b': {'size_gb': 8.0, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'llava:13b'},
            
            # Reasoning Specialist
            'qwq-32b': {'size_gb': 20, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwq:32b'},
            
            # Latest General Models
            'llama-3.1-8b': {'size_gb': 5.0, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'llama3.1:8b'},
            'llama-3.1-70b': {'size_gb': 43, 'speed_rating': 3, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'llama3.1:70b'},
            'gemma3-9b': {'size_gb': 5.5, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'gemma3:9b'},
            'phi4-14b': {'size_gb': 9.1, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'phi4:14b'},
            
            # Efficient/Lightweight Options
            'qwen3-1.7b': {'size_gb': 1.2, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'qwen3:1.7b'},
            'gemma3-4b': {'size_gb': 2.5, 'speed_rating': 5, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'gemma3:4b'},
            'mistral-nemo-12b': {'size_gb': 7.5, 'speed_rating': 4, 'format': 'GGUF (Q4_K_M)', 'ollama_name': 'mistral-nemo:12b'}
        }
        
        # Cache for real-time pricing to avoid excessive API calls
        self.pricing_cache = {}
        self.pricing_cache_timestamp = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Initialize dynamic model discovery
        self.discovered_models = {
            'openai': [],
            'anthropic': [],
            'xai': [],
            'google': [],
            'ollama': []
        }

    def discover_available_models(self) -> Dict[str, List[Dict]]:
        """Dynamically discover all available models from APIs and local installations."""
        print("🔍 Starting dynamic model discovery...")
        
        discovered = {}
        
        # Discover hosted models
        for provider in ['openai', 'anthropic', 'xai', 'google']:
            try:
                discovered[provider] = self._discover_provider_models(provider)
                print(f"✅ Discovered {len(discovered[provider])} models from {provider}")
            except Exception as e:
                print(f"❌ Failed to discover {provider} models: {e}")
                discovered[provider] = []
        
        # Discover local models
        try:
            discovered['ollama'] = self._discover_ollama_models()
            print(f"✅ Discovered {len(discovered['ollama'])} local Ollama models")
        except Exception as e:
            print(f"❌ Failed to discover Ollama models: {e}")
            discovered['ollama'] = []
        
        # Update internal storage
        self.discovered_models = discovered
        return discovered

    def _discover_provider_models(self, provider: str) -> List[Dict]:
        """Discover models from a specific provider's API."""
        endpoint = self.api_endpoints.get(provider)
        if not endpoint:
            return []
        
        headers = self._get_api_headers(provider)
        if not headers:
            print(f"⚠️  No API key for {provider}, skipping discovery")
            return []
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                if provider == 'openai':
                    return self._parse_openai_models(data)
                elif provider == 'anthropic':
                    return self._parse_anthropic_models(data)
                elif provider == 'xai':
                    return self._parse_xai_models(data)
                elif provider == 'google':
                    return self._parse_google_models(data)
            else:
                print(f"❌ API error for {provider}: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error discovering {provider} models: {e}")
            return []

    def _discover_ollama_models(self) -> List[Dict]:
        """Discover locally available Ollama models."""
        try:
            # Check if Ollama is running
            response = requests.get(self.api_endpoints['ollama'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                # Also discover available models from Ollama library
                available_models = self._discover_ollama_library()
                
                return self._parse_ollama_models(models, available_models)
            else:
                print(f"❌ Ollama not running (status: {response.status_code})")
                return self._discover_ollama_library()  # Return library models as available
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            return self._discover_ollama_library()  # Return library models as available

    def _discover_ollama_library(self) -> List[Dict]:
        """Discover available models from Ollama library."""
        try:
            # Use Ollama's search API or parse library page
            library_url = "https://ollama.com/api/library"
            response = requests.get(library_url, timeout=30)
            if response.status_code == 200:
                return response.json().get('models', [])
        except:
            pass
        
        # Fallback to known popular models from 2025
        return [
            {'name': 'llama3.3:70b', 'size': '43GB', 'description': 'GPT-4 class performance'},
            {'name': 'deepseek-r1:8b', 'size': '5GB', 'description': 'Advanced reasoning model'},
            {'name': 'qwen3:8b', 'size': '5.2GB', 'description': 'Latest Qwen generation'},
            {'name': 'qwen2.5-coder:7b', 'size': '4.7GB', 'description': 'Specialized coding model'},
            {'name': 'qwen2.5vl:7b', 'size': '6GB', 'description': 'Vision-language model'},
        ]

    def _get_api_headers(self, provider: str) -> Optional[Dict[str, str]]:
        """Get appropriate headers for API requests."""
        if provider == 'openai' and self.openai_api_key:
            return {'Authorization': f'Bearer {self.openai_api_key}', 'Content-Type': 'application/json'}
        elif provider == 'anthropic' and self.anthropic_api_key:
            return {'x-api-key': self.anthropic_api_key, 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01'}
        elif provider == 'xai' and self.xai_api_key:
            return {'Authorization': f'Bearer {self.xai_api_key}', 'Content-Type': 'application/json'}
        elif provider == 'google' and self.google_api_key:
            return {'Authorization': f'Bearer {self.google_api_key}', 'Content-Type': 'application/json'}
        return None

    def _parse_openai_models(self, data: Dict) -> List[Dict]:
        """Parse OpenAI models API response."""
        models = []
        for model in data.get('data', []):
            models.append({
                'id': model.get('id'),
                'created': model.get('created'),
                'owned_by': model.get('owned_by'),
                'object': model.get('object', 'model')
            })
        return models

    def _parse_anthropic_models(self, data: Dict) -> List[Dict]:
        """Parse Anthropic models API response."""
        models = []
        for model in data.get('data', []):
            models.append({
                'id': model.get('id'),
                'display_name': model.get('display_name'),
                'created_at': model.get('created_at'),
                'type': model.get('type', 'model')
            })
        return models

    def _parse_xai_models(self, data: Dict) -> List[Dict]:
        """Parse xAI models API response."""
        models = []
        for model in data.get('data', []):
            models.append({
                'id': model.get('id'),
                'created': model.get('created'),
                'owned_by': model.get('owned_by', 'xai'),
                'object': model.get('object', 'model')
            })
        return models

    def _parse_google_models(self, data: Dict) -> List[Dict]:
        """Parse Google models API response."""
        models = []
        for model in data.get('models', []):
            models.append({
                'name': model.get('name'),
                'displayName': model.get('displayName'),
                'description': model.get('description'),
                'inputTokenLimit': model.get('inputTokenLimit'),
                'outputTokenLimit': model.get('outputTokenLimit')
            })
        return models

    def _parse_ollama_models(self, local_models: List[Dict], available_models: List[Dict]) -> List[Dict]:
        """Parse Ollama models combining local and available."""
        all_models = []
        
        # Add locally installed models
        for model in local_models:
            all_models.append({
                'name': model.get('name'),
                'size': model.get('size'),
                'digest': model.get('digest'),
                'modified_at': model.get('modified_at'),
                'status': 'installed'
            })
        
        # Add available models not yet installed
        local_names = {m.get('name') for m in local_models}
        for model in available_models:
            if model.get('name') not in local_names:
                model['status'] = 'available'
                all_models.append(model)
        
        return all_models

    def _convert_ollama_name_to_id(self, ollama_name: str) -> str:
        """Convert Ollama model name to our internal ID format."""
        # Examples: llama3.3:70b -> llama-3.3-70b, qwen2.5-coder:7b -> qwen2.5-coder-7b
        return ollama_name.replace(':', '-').replace('.', '-').lower()

    def _build_dynamic_local_model_info(self, model_id: str, ollama_name: str, model_info: Dict, 
                                       tools_available: Dict, llama_cpp_available: bool, 
                                       model_paths: Dict) -> Dict[str, Any]:
        """Build local model information from dynamically discovered data."""
        
        # Extract size from model info
        size_str = model_info.get('size', '0B')
        size_gb = self._parse_size_to_gb(size_str)
        
        # Determine format and speed rating
        format_info = 'GGUF (Q4_K_M)'  # Default for Ollama models
        speed_rating = self._estimate_speed_rating(size_gb)
        
        # Dynamic capability detection
        capabilities = self._detect_local_model_capabilities(model_id)
        
        # Generate dynamic strengths
        strengths = self._generate_dynamic_strengths(model_id, ollama_name, model_info)
        
        # Estimate context window based on model name
        context_window = self._estimate_context_window(model_id)
        
        # Check if model is installed
        status = model_info.get('status', 'available')
        installation_status = 'ready' if status == 'installed' else 'available'
        
        return {
            'id': model_id,
            'provider': 'local',
            'type': 'local',
            'ollama_name': ollama_name,
            'pricing': {'input': 0.0, 'output': 0.0},
            'context_window': context_window,
            'strengths': strengths,
            'capabilities': capabilities,
            'cost_per_1m_tokens': {'input': 0, 'output': 0},
            'size_gb': size_gb,
            'speed_rating': speed_rating,
            'format': format_info,
            'tools_available': tools_available,
            'llama_cpp_available': llama_cpp_available,
            'estimated_ram_usage': f"{size_gb * 1.2:.1f} GB",
            'local_files_found': 1 if status == 'installed' else 0,
            'file_paths': [],
            'installation_status': installation_status,
            'release_date': self._estimate_release_date(model_id),
            'discovery_method': 'dynamic_ollama',
            'last_modified': model_info.get('modified_at', 'Unknown')
        }

    def _parse_size_to_gb(self, size_str) -> float:
        """Parse size string to GB."""
        if not size_str:
            return 5.0  # Default size
        
        # Handle numeric inputs
        if isinstance(size_str, (int, float)):
            return float(size_str) / (1024**3)  # Assume bytes
        
        # Convert to string and handle
        size_str = str(size_str).upper()
        if 'GB' in size_str:
            return float(size_str.replace('GB', '').strip())
        elif 'MB' in size_str:
            return float(size_str.replace('MB', '').strip()) / 1024
        elif 'B' in size_str and 'GB' not in size_str and 'MB' not in size_str:
            return float(size_str.replace('B', '').strip()) / (1024**3)
        else:
            # Try to extract number and assume GB
            import re
            numbers = re.findall(r'\d+\.?\d*', size_str)
            return float(numbers[0]) if numbers else 5.0

    def _estimate_speed_rating(self, size_gb: float) -> int:
        """Estimate speed rating based on model size."""
        if size_gb < 2:
            return 5  # Very fast
        elif size_gb < 8:
            return 4  # Fast
        elif size_gb < 20:
            return 3  # Medium
        elif size_gb < 50:
            return 2  # Slow
        else:
            return 1  # Very slow

    def _generate_dynamic_strengths(self, model_id: str, ollama_name: str, model_info: Dict) -> str:
        """Generate strengths description based on model characteristics."""
        strengths = []
        
        model_lower = model_id.lower()
        
        # Model-specific strengths
        if 'deepseek-r1' in model_lower:
            strengths.append("Advanced reasoning and chain-of-thought capabilities")
        elif 'qwen3' in model_lower:
            strengths.append("Latest generation multilingual model with excellent performance")
        elif 'coder' in model_lower:
            strengths.append("Specialized for code generation and programming tasks")
        elif 'vl' in model_lower or 'vision' in model_lower:
            strengths.append("Multimodal vision-language understanding")
        elif 'llama' in model_lower:
            strengths.append("Reliable general-purpose model optimized for Apple Silicon")
        elif 'qwq' in model_lower:
            strengths.append("Specialized reasoning model with enhanced logical thinking")
        elif 'gemma' in model_lower:
            strengths.append("Google's safe and efficient language model")
        elif 'phi' in model_lower:
            strengths.append("Microsoft's compact model with strong reasoning")
        elif 'mistral' in model_lower:
            strengths.append("Excellent multilingual capabilities and efficiency")
        else:
            strengths.append("General-purpose language model")
        
        # Size-based strengths
        description = model_info.get('description', '')
        if description:
            strengths.append(description)
        
        return "; ".join(strengths) if strengths else "Local language model for privacy and offline use"

    def _estimate_context_window(self, model_id: str) -> int:
        """Estimate context window based on model name and generation."""
        model_lower = model_id.lower()
        
        # Latest models typically have larger context windows
        if any(term in model_lower for term in ['3.3', 'r1', 'qwen3', 'phi4', 'gemma3']):
            return 131072  # 128K
        elif any(term in model_lower for term in ['3.1', '2.5']):
            return 131072  # 128K
        elif 'vl' in model_lower or 'vision' in model_lower:
            return 65536   # 64K for vision models
        else:
            return 32768   # 32K default

    def _estimate_release_date(self, model_id: str) -> str:
        """Estimate release date based on model name."""
        model_lower = model_id.lower()
        
        # Try to extract date from model name
        import re
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', model_id)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        
        # Estimate based on model family
        if 'r1' in model_lower or 'qwen3' in model_lower:
            return '2025-01-20'
        elif '3.3' in model_lower:
            return '2024-12-06'
        elif '2.5' in model_lower:
            return '2024-12-01'
        elif '3.1' in model_lower:
            return '2024-07-23'
        else:
            return '2024-01-01'

    def get_real_time_pricing(self, provider: str, model_id: str) -> Dict[str, float]:
        """Fetch real-time pricing for a specific model from multiple sources."""
        cache_key = f"{provider}:{model_id}"
        current_time = time.time()
        
        # Check cache first
        if (cache_key in self.pricing_cache and 
            cache_key in self.pricing_cache_timestamp and
            current_time - self.pricing_cache_timestamp[cache_key] < self.cache_duration):
            return self.pricing_cache[cache_key]
        
        print(f"🔍 Fetching real-time pricing for {provider}/{model_id}...")
        
        pricing = {'input': 0.0, 'output': 0.0}
        
        try:
            # For now, prioritize fallback pricing to ensure we have valid data
            # Real-time pricing can be enabled later once we have reliable external sources
            pricing = self._get_fallback_pricing(provider, model_id)
            
            # If fallback pricing is empty, try external sources
            if not pricing or (pricing.get('input', 0) == 0 and pricing.get('output', 0) == 0):
                if provider == 'openai':
                    pricing = self._fetch_openai_pricing(model_id)
                elif provider == 'anthropic':
                    pricing = self._fetch_anthropic_pricing(model_id)
                elif provider == 'xai':
                    pricing = self._fetch_xai_pricing(model_id)
                elif provider == 'google':
                    pricing = self._fetch_google_pricing(model_id)
                else:
                    pricing = {'input': 0.0, 'output': 0.0}
            
            # Validate pricing makes sense - but always use fallback if pricing is invalid
            if self._validate_pricing_data(pricing) and (pricing['input'] > 0 or pricing['output'] > 0):
                self.pricing_cache[cache_key] = pricing
                self.pricing_cache_timestamp[cache_key] = current_time
                print(f"✅ Updated pricing for {model_id}: IN=${pricing['input']:.3f}, OUT=${pricing['output']:.3f} per 1K tokens")
            else:
                print(f"⚠️  Real-time pricing failed for {model_id}, using fallback")
                pricing = self._get_fallback_pricing(provider, model_id)
                if pricing.get('input', 0) > 0 or pricing.get('output', 0) > 0:
                    print(f"📋 Fallback pricing for {model_id}: IN=${pricing.get('input', 0):.3f}, OUT=${pricing.get('output', 0):.3f} per 1K tokens")
                else:
                    print(f"❌ No pricing available for {model_id}")
                
        except Exception as e:
            print(f"❌ Error fetching pricing for {model_id}: {e}")
            pricing = self._get_fallback_pricing(provider, model_id)
        
        return pricing

    def _fetch_openai_pricing(self, model_id: str) -> Dict[str, float]:
        """Fetch OpenAI pricing from official sources."""
        # Try official pricing API endpoints if they exist
        pricing_sources = [
            self._check_openai_api_pricing,
            self._scrape_openai_pricing_page,
            self._get_community_pricing_data
        ]
        
        for source_func in pricing_sources:
            try:
                pricing = source_func(model_id)
                if pricing and (pricing['input'] > 0 or pricing['output'] > 0):
                    return pricing
            except Exception as e:
                continue
        
        return self._get_fallback_pricing('openai', model_id)

    def _check_openai_api_pricing(self, model_id: str) -> Dict[str, float]:
        """Try to get pricing from OpenAI API if available."""
        if not self.openai_api_key:
            return {'input': 0.0, 'output': 0.0}
        
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Check if OpenAI has a pricing endpoint
            response = requests.get(f'https://api.openai.com/v1/models/{model_id}', headers=headers, timeout=10)
            if response.status_code == 200:
                model_data = response.json()
                # Look for pricing information in model metadata
                if 'pricing' in model_data:
                    return {
                        'input': model_data['pricing'].get('input_per_1k', 0.0),
                        'output': model_data['pricing'].get('output_per_1k', 0.0)
                    }
        except:
            pass
            
        return {'input': 0.0, 'output': 0.0}

    def _scrape_openai_pricing_page(self, model_id: str) -> Dict[str, float]:
        """Attempt to get pricing from OpenAI's official pricing page."""
        try:
            # Use a web scraping approach with requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            # This would normally scrape the pricing page, but due to rate limiting
            # and anti-bot measures, we'll use the WebSearch approach instead
            return self._get_pricing_from_web_search(model_id, 'openai')
            
        except Exception as e:
            return {'input': 0.0, 'output': 0.0}

    def _get_pricing_from_web_search(self, model_id: str, provider: str) -> Dict[str, float]:
        """Get pricing by searching for official pricing information using external APIs."""
        try:
            # Try multiple external pricing sources
            pricing_sources = [
                self._check_openrouter_pricing,
                self._check_litellm_pricing,
                self._search_official_docs,
                self._get_fallback_pricing
            ]
            
            for source in pricing_sources:
                try:
                    pricing = source(provider, model_id)
                    if pricing and (pricing.get('input', 0) > 0 or pricing.get('output', 0) > 0):
                        return pricing
                except Exception as e:
                    continue
            
            # If all else fails, use fallback pricing
            return self._get_fallback_pricing(provider, model_id)
            
        except Exception:
            return {'input': 0.0, 'output': 0.0}

    def _check_openrouter_pricing(self, provider: str, model_id: str) -> Dict[str, float]:
        """Check OpenRouter API for pricing information."""
        try:
            # OpenRouter aggregates many model providers and has pricing info
            response = requests.get('https://openrouter.ai/api/v1/models', timeout=10)
            if response.status_code == 200:
                models = response.json().get('data', [])
                
                for model in models:
                    model_name = model.get('id', '')
                    # Try to match model names across providers
                    if (model_id in model_name or 
                        model_name.split('/')[-1] == model_id or
                        any(part in model_name for part in model_id.split('-')[:2])):
                        
                        pricing = model.get('pricing', {})
                        if pricing:
                            # OpenRouter prices are typically per 1M tokens, convert to 1K
                            return {
                                'input': float(pricing.get('prompt', 0)) / 1000,
                                'output': float(pricing.get('completion', 0)) / 1000
                            }
        except Exception as e:
            pass
        
        return {'input': 0.0, 'output': 0.0}

    def _check_litellm_pricing(self, provider: str, model_id: str) -> Dict[str, float]:
        """Check LiteLLM pricing database."""
        try:
            # LiteLLM maintains pricing for many providers
            # This is a simplified example - actual implementation would query their API
            litellm_pricing_map = {
                'openai': {
                    'gpt-4o': {'input': 5.0, 'output': 20.0},
                    'gpt-4o-mini': {'input': 0.15, 'output': 0.6},
                    'gpt-4-turbo': {'input': 10.0, 'output': 30.0},
                    'gpt-4': {'input': 30.0, 'output': 60.0},
                    'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5},
                    'o1': {'input': 15.0, 'output': 60.0},
                    'o1-mini': {'input': 3.0, 'output': 12.0},
                    'o1-pro': {'input': 0.15, 'output': 0.6},  # $150/$600 per 1M = $0.15/$0.6 per 1K
                    'o1-pro-2025-03-19': {'input': 0.15, 'output': 0.6},  # $150/$600 per 1M = $0.15/$0.6 per 1K
                },
                'anthropic': {
                    'claude-3-5-sonnet-20241022': {'input': 3.0, 'output': 15.0},
                    'claude-3-opus-20240229': {'input': 15.0, 'output': 75.0},
                    'claude-3-sonnet-20240229': {'input': 3.0, 'output': 15.0},
                    'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},
                },
                'xai': {
                    'grok-beta': {'input': 5.0, 'output': 15.0},
                    'grok-vision-beta': {'input': 5.0, 'output': 15.0},
                },
                'google': {
                    'gemini-pro': {'input': 0.5, 'output': 1.5},
                    'gemini-pro-vision': {'input': 0.5, 'output': 1.5},
                }
            }
            
            if provider in litellm_pricing_map and model_id in litellm_pricing_map[provider]:
                return litellm_pricing_map[provider][model_id]
                
        except Exception:
            pass
        
        return {'input': 0.0, 'output': 0.0}

    def _search_official_docs(self, provider: str, model_id: str) -> Dict[str, float]:
        """Search official documentation for pricing using web search."""
        try:
            # Search for official pricing documentation
            search_queries = [
                f"{provider} {model_id} pricing API cost per token",
                f"{provider} pricing {model_id} official documentation",
                f"OpenAI {model_id} price per 1000 tokens" if provider == 'openai' else f"{provider} {model_id} token pricing"
            ]
            
            # This would implement actual web search functionality
            # For now, return empty to fall through to fallback
            return {'input': 0.0, 'output': 0.0}
            
        except Exception:
            return {'input': 0.0, 'output': 0.0}

    def _get_community_pricing_data(self, model_id: str) -> Dict[str, float]:
        """Fetch pricing from community-maintained pricing databases."""
        try:
            # Check multiple community sources for pricing data
            sources = [
                'https://openai-community-pricing.com/api/pricing',  # Example endpoint
                'https://llm-pricing-tracker.com/api/models',  # Example endpoint
            ]
            
            for source in sources:
                try:
                    response = requests.get(source, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if model_id in data:
                            return {
                                'input': data[model_id].get('input_per_1k', 0.0),
                                'output': data[model_id].get('output_per_1k', 0.0)
                            }
                except:
                    continue
                    
        except Exception:
            pass
            
        return {'input': 0.0, 'output': 0.0}

    def _fetch_anthropic_pricing(self, model_id: str) -> Dict[str, float]:
        """Fetch Anthropic pricing from official sources."""
        try:
            # Anthropic doesn't have a public pricing API, so we'll use web search
            return self._get_pricing_from_web_search(model_id, 'anthropic')
        except:
            return self._get_fallback_pricing('anthropic', model_id)

    def _fetch_xai_pricing(self, model_id: str) -> Dict[str, float]:
        """Fetch xAI pricing from official sources."""
        try:
            if self.xai_api_key:
                headers = {
                    'Authorization': f'Bearer {self.xai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Try xAI's models endpoint if it includes pricing
                response = requests.get('https://api.x.ai/v1/models', headers=headers, timeout=10)
                if response.status_code == 200:
                    models = response.json().get('data', [])
                    for model in models:
                        if model.get('id') == model_id and 'pricing' in model:
                            return {
                                'input': model['pricing'].get('input_per_1k', 0.0),
                                'output': model['pricing'].get('output_per_1k', 0.0)
                            }
            
            return self._get_pricing_from_web_search(model_id, 'xai')
        except:
            return self._get_fallback_pricing('xai', model_id)

    def _fetch_google_pricing(self, model_id: str) -> Dict[str, float]:
        """Fetch Google pricing from official sources."""
        try:
            return self._get_pricing_from_web_search(model_id, 'google')
        except:
            return self._get_fallback_pricing('google', model_id)

    def _validate_pricing_data(self, pricing: Dict[str, float]) -> bool:
        """Validate that pricing data makes sense."""
        if not isinstance(pricing, dict):
            return False
        
        input_price = pricing.get('input', 0)
        output_price = pricing.get('output', 0)
        
        # Basic sanity checks
        if not isinstance(input_price, (int, float)) or not isinstance(output_price, (int, float)):
            return False
        
        # Prices should be non-negative 
        if input_price < 0 or output_price < 0:
            return False
        
        # Prices above $1000 per 1K tokens are likely errors (very generous limit)
        if input_price > 1000 or output_price > 1000:
            return False
        
        # Prices below $0.0001 are likely calculation errors (too small)
        if (input_price > 0 and input_price < 0.0001) or (output_price > 0 and output_price < 0.0001):
            return False
        
        return True

    def _get_fallback_pricing(self, provider: str, model_id: str) -> Dict[str, float]:
        """Get fallback pricing from hardcoded data."""
        return self.pricing_info[provider].get(model_id, {'input': 0.0, 'output': 0.0})
    
    def _get_model_release_date(self, provider: str, model_id: str) -> str:
        """Get model release date if available."""
        return self.model_release_dates.get(provider, {}).get(model_id, 'Unknown')

    def check_api_keys(self):
        """Verify that available API keys are present."""
        available_keys = []
        missing_keys = []
        
        if self.openai_api_key:
            available_keys.append('OPENAI_API_KEY')
        else:
            missing_keys.append('OPENAI_API_KEY')
            
        if self.anthropic_api_key:
            available_keys.append('ANTHROPIC_API_KEY')
        else:
            missing_keys.append('ANTHROPIC_API_KEY')
            
        if self.xai_api_key:
            available_keys.append('XAI_API_KEY')
        else:
            missing_keys.append('XAI_API_KEY')
            
        if self.google_api_key:
            available_keys.append('GOOGLE_API_KEY') 
        else:
            missing_keys.append('GOOGLE_API_KEY')
            
        print(f"✅ Available API keys: {', '.join(available_keys) if available_keys else 'None'}")
        if missing_keys:
            print(f"⚠️  Missing API keys: {', '.join(missing_keys)} (will use fallback data)")
        
        return len(available_keys) > 0

    def get_openai_models(self) -> Dict[str, Any]:
        """Dynamically fetch available models from OpenAI API."""
        print("🔍 Fetching OpenAI models...")
        
        if not self.openai_api_key:
            print("⚠️  No OpenAI API key, using fallback data")
            return self._get_openai_fallback()
        
        try:
            # Use dynamic discovery
            discovered_models = self._discover_provider_models('openai')
            if not discovered_models:
                return self._get_openai_fallback()
            
            # Filter for relevant chat models and add our enhanced information
            relevant_models = {}
            for model in discovered_models:
                model_id = model['id']
                if any(name in model_id for name in ['gpt-4', 'gpt-3.5', 'o1']):
                    relevant_models[model_id] = self._build_model_info('openai', model_id, model)
            
            print(f"✅ Found {len(relevant_models)} OpenAI models")
            return relevant_models
            
        except Exception as e:
            print(f"❌ Error fetching OpenAI models (using fallback): {e}")
            return self._get_openai_fallback()

    def _get_openai_fallback(self) -> Dict[str, Any]:
        """Fallback OpenAI model data."""
        fallback_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo', 'o1-preview', 'o1-mini']
        return {model_id: self._build_model_info('openai', model_id) for model_id in fallback_models}

    def get_anthropic_models(self) -> Dict[str, Any]:
        """Dynamically fetch available models from Anthropic API."""
        print("🔍 Fetching Anthropic models...")
        
        try:
            # Use dynamic discovery first
            discovered_models = self._discover_provider_models('anthropic')
            if discovered_models:
                models = {}
                for model in discovered_models:
                    model_id = model.get('id', model.get('name'))
                    if model_id and 'claude' in model_id.lower():
                        models[model_id] = self._build_model_info('anthropic', model_id, model)
                
                if models:
                    print(f"✅ Found {len(models)} Anthropic models via API")
                    return models
        except Exception as e:
            print(f"⚠️  API discovery failed: {e}")
        
        # Fallback to known models if API discovery fails
        known_models = [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-sonnet-20240620', 
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]
        
        models = {model_id: self._build_model_info('anthropic', model_id) for model_id in known_models}
        
        print(f"✅ Found {len(models)} Anthropic models (fallback)")
        return models

    def get_xai_models(self) -> Dict[str, Any]:
        """Dynamically fetch available models from xAI API."""
        print("🔍 Fetching xAI (Grok) models...")
        
        try:
            # Use dynamic discovery first
            discovered_models = self._discover_provider_models('xai')
            if discovered_models:
                models = {}
                for model in discovered_models:
                    model_id = model.get('id', model.get('name'))
                    if model_id and 'grok' in model_id.lower():
                        models[model_id] = self._build_model_info('xai', model_id, model)
                
                if models:
                    print(f"✅ Found {len(models)} xAI models via API")
                    return models
        except Exception as e:
            print(f"⚠️  API discovery failed: {e}")
        
        # Fallback to known models
        print("⚠️  Using fallback xAI models")
        return self._get_xai_fallback()

    def _get_xai_fallback(self) -> Dict[str, Any]:
        """Fallback xAI model data."""
        fallback_models = ['grok-beta', 'grok-vision-beta', 'grok-4']
        return {model_id: self._build_model_info('xai', model_id) for model_id in fallback_models}

    def get_google_models(self) -> Dict[str, Any]:
        """Dynamically fetch available models from Google API."""
        print("🔍 Fetching Google (Gemini) models...")
        
        try:
            # Use dynamic discovery first
            discovered_models = self._discover_provider_models('google')
            if discovered_models:
                models = {}
                for model in discovered_models:
                    model_id = model.get('name', model.get('id'))
                    if model_id and 'gemini' in model_id.lower():
                        models[model_id] = self._build_model_info('google', model_id, model)
                
                if models:
                    print(f"✅ Found {len(models)} Google models via API")
                    return models
        except Exception as e:
            print(f"⚠️  API discovery failed: {e}")
        
        # Fallback to known models
        known_models = [
            'gemini-2.5-pro',
            'gemini-2.5-flash',
            'gemini-pro',
            'gemini-pro-vision'
        ]
        
        models = {model_id: self._build_model_info('google', model_id) for model_id in known_models}
        
        print(f"✅ Found {len(models)} Google models (fallback)")
        return models

    def get_local_models(self) -> Dict[str, Any]:
        """Dynamically discover and get information about locally available models."""
        print("🔍 Checking local models...")
        
        local_models = {}
        
        # Check for common local model tools
        tools_available = {}
        tool_import_map = {
            'llama-cpp-python': 'llama_cpp',
            'mlc-llm': 'mlc_llm', 
            'ctransformers': 'ctransformers',
            'transformers': 'transformers'
        }
        
        for tool, import_name in tool_import_map.items():
            try:
                # Check if the tool is available in Python environment
                __import__(import_name)
                tools_available[tool] = True
                print(f"   ✅ {tool} available")
            except ImportError:
                tools_available[tool] = False
                print(f"   ❌ {tool} not available")
        
        # Check for llama.cpp binary
        llama_cpp_available = shutil.which('llama-cpp-server') is not None
        if llama_cpp_available:
            print("   ✅ llama-cpp-server binary available")
        else:
            print("   ❌ llama-cpp-server binary not found")
        
        # Check for actual model files in common locations
        model_paths = self._scan_for_local_models()
        
        # Discover available Ollama models dynamically
        try:
            discovered_ollama = self._discover_ollama_models()
            print(f"   🔍 Discovered {len(discovered_ollama)} Ollama models")
            
            # Build local model info for discovered models
            for model_info in discovered_ollama:
                model_name = model_info.get('name')
                if model_name:
                    # Convert Ollama name to our format
                    model_id = self._convert_ollama_name_to_id(model_name)
                    local_models[model_id] = self._build_dynamic_local_model_info(
                        model_id, model_name, model_info, tools_available, llama_cpp_available, model_paths
                    )
        except Exception as e:
            print(f"   ⚠️  Ollama discovery failed: {e}")
        
        # Also include our predefined models for compatibility
        for model_id in self.local_model_specs.keys():
            if model_id not in local_models:
                local_models[model_id] = self._build_local_model_info(model_id, tools_available, llama_cpp_available, model_paths)
        
        print(f"✅ Found {len(local_models)} local model configurations")
        return local_models

    def _scan_for_local_models(self) -> Dict[str, List[str]]:
        """Scan common directories for local model files."""
        model_paths = {}
        
        # Common model storage locations
        common_paths = [
            os.path.expanduser("~/.cache/huggingface/hub"),
            os.path.expanduser("~/.cache/llama.cpp"),
            os.path.expanduser("~/models"),
            os.path.expanduser("~/Downloads"),
            "./models",
            "./local_models"
        ]
        
        print("   🔍 Scanning for local model files...")
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                try:
                    for root, dirs, files in os.walk(base_path):
                        for file in files:
                            if file.endswith(('.gguf', '.bin', '.safetensors', '.pt', '.pth')):
                                file_path = os.path.join(root, file)
                                # Extract model name from file path
                                model_name = self._extract_model_name_from_path(file_path)
                                if model_name:
                                    if model_name not in model_paths:
                                        model_paths[model_name] = []
                                    model_paths[model_name].append(file_path)
                                    print(f"      📁 Found: {model_name} at {file_path}")
                except (PermissionError, OSError):
                    continue
        
        if not model_paths:
            print("   ℹ️  No local model files found in common locations")
        
        return model_paths
    
    def _extract_model_name_from_path(self, file_path: str) -> Optional[str]:
        """Extract model name from file path."""
        file_name = os.path.basename(file_path).lower()
        
        # Common model name patterns
        model_patterns = {
            'llama': ['llama', 'llama-2', 'llama-3'],
            'mistral': ['mistral', 'mistral-7b'],
            'mixtral': ['mixtral', 'mixtral-8x7b'],
            'code-llama': ['code-llama', 'codellama'],
            'phi': ['phi-3', 'phi3'],
            'gemma': ['gemma'],
            'falcon': ['falcon'],
            'mpt': ['mpt']
        }
        
        for model_type, patterns in model_patterns.items():
            for pattern in patterns:
                if pattern in file_name:
                    return model_type
        
        return None

    def _build_model_info(self, provider: str, model_id: str, api_model: Optional[Dict] = None) -> Dict[str, Any]:
        """Build comprehensive model information with real-time pricing."""
        
        # Get real-time pricing first
        real_time_pricing = self.get_real_time_pricing(provider, model_id)
        
        # Validate the pricing data
        if self._validate_pricing_data(real_time_pricing):
            pricing = real_time_pricing
        else:
            # Fall back to hardcoded pricing if real-time fails validation
            pricing = self.pricing_info[provider].get(model_id, {'input': 0.0, 'output': 0.0})
            print(f"⚠️  Using fallback pricing for {model_id}: ${pricing.get('input', 0):.3f}/${pricing.get('output', 0):.3f}")
        
        # Dynamic context window detection
        context_window = self._detect_context_window(provider, model_id, api_model)
        
        # Dynamic strengths generation
        strengths = self._generate_model_strengths(provider, model_id, api_model)
        
        # Dynamic capability detection
        capabilities = self._detect_model_capabilities(provider, model_id, api_model)
        
        # Ensure pricing values are numeric
        input_price = pricing.get('input', 0) if isinstance(pricing.get('input'), (int, float)) else 0
        output_price = pricing.get('output', 0) if isinstance(pricing.get('output'), (int, float)) else 0
        
        info = {
            'id': model_id,
            'provider': provider,
            'pricing': {
                'input': input_price,
                'output': output_price
            },
            'context_window': context_window,
            'strengths': strengths,
            'capabilities': capabilities,
            'cost_per_1m_tokens': {
                'input': input_price * 1000,  # Convert per 1K to per 1M
                'output': output_price * 1000
            },
            'pricing_source': 'real-time' if self._validate_pricing_data(real_time_pricing) else 'fallback',
            'last_price_check': datetime.now().isoformat()
        }
        
        if api_model:
            info.update({
                'created': api_model.get('created'),
                'owned_by': api_model.get('owned_by')
            })
        else:
            # For non-OpenAI models, add release date from our data
            release_date = self._get_model_release_date(provider, model_id)
            if release_date != 'Unknown':
                info['release_date'] = release_date
        
        return info

    def _detect_context_window(self, provider: str, model_id: str, api_model: Optional[Dict] = None) -> int:
        """Dynamically detect context window from API metadata or model name patterns."""
        
        # First try to get from API metadata
        if api_model:
            # Some APIs include context length in the response
            if 'context_length' in api_model:
                return api_model['context_length']
            if 'max_tokens' in api_model:
                return api_model['max_tokens']
            if 'context_window' in api_model:
                return api_model['context_window']
        
        # Pattern-based detection from model names
        context_patterns = {
            # OpenAI patterns
            'gpt-4o': 128000,
            'gpt-4-turbo': 128000,
            'gpt-4': 8192,  # Original GPT-4
            'gpt-4-0613': 8192,
            'gpt-3.5-turbo-16k': 16384,
            'gpt-3.5-turbo': 16385,
            'gpt-3.5-turbo-instruct': 4096,
            'o1': 200000,
            'o1-mini': 128000,
            'o1-pro': 200000,
            
            # Anthropic patterns
            'claude-3': 200000,  # All Claude 3 models
            
            # xAI patterns
            'grok': 128000,  # Most Grok models
            
            # Google patterns
            'gemini-2.5': 1000000,  # Gemini 2.5 series
            'gemini-pro': 128000,
        }
        
        # Check for pattern matches
        for pattern, context_size in context_patterns.items():
            if pattern in model_id.lower():
                return context_size
        
        # Fall back to hardcoded values if available
        if hasattr(self, 'context_windows') and provider in self.context_windows:
            return self.context_windows[provider].get(model_id, 128000)
        
        # Default fallback
        return 128000

    def _generate_model_strengths(self, provider: str, model_id: str, api_model: Optional[Dict] = None) -> str:
        """Dynamically generate model strengths based on model name and metadata."""
        
        model_lower = model_id.lower()
        strengths = []
        
        # Analyze model name for capabilities
        if 'vision' in model_lower or 'image' in model_lower:
            strengths.append("multimodal vision capabilities")
        
        if 'audio' in model_lower or 'realtime' in model_lower:
            strengths.append("audio processing and real-time interaction")
        
        if 'search' in model_lower:
            strengths.append("web search integration")
            
        if 'transcribe' in model_lower:
            strengths.append("audio transcription")
            
        if 'tts' in model_lower:
            strengths.append("text-to-speech generation")
        
        # Provider-specific patterns
        if provider == 'openai':
            if 'gpt-4o' in model_lower:
                strengths.append("latest multimodal model, excellent for complex reasoning")
            elif 'gpt-4' in model_lower:
                if 'turbo' in model_lower:
                    strengths.append("advanced reasoning with large context window")
                else:
                    strengths.append("strong reasoning and creative tasks")
            elif 'gpt-3.5' in model_lower:
                strengths.append("fast and cost-effective for simpler tasks")
            elif 'o1' in model_lower:
                if 'mini' in model_lower:
                    strengths.append("reasoning-focused model optimized for coding and math")
                elif 'pro' in model_lower:
                    strengths.append("advanced reasoning for complex problem-solving")
                else:
                    strengths.append("sophisticated reasoning capabilities")
                    
        elif provider == 'anthropic':
            if 'claude-3-5' in model_lower:
                strengths.append("latest Claude with excellent coding and analysis capabilities")
            elif 'claude-3-opus' in model_lower:
                strengths.append("most capable Claude model for complex reasoning tasks")
            elif 'claude-3-sonnet' in model_lower:
                strengths.append("balanced performance and speed for most tasks")
            elif 'claude-3-haiku' in model_lower:
                strengths.append("fastest Claude model, good for simple tasks and high volume")
                
        elif provider == 'xai':
            if 'grok-4' in model_lower:
                strengths.append("STEM and science focused, strong reasoning")
            elif 'grok-3' in model_lower:
                if 'mini' in model_lower:
                    strengths.append("compact model for efficient processing")
                elif 'fast' in model_lower:
                    strengths.append("optimized for speed and quick responses")
                else:
                    strengths.append("advanced reasoning capabilities")
            elif 'grok-2' in model_lower:
                strengths.append("balanced reasoning and performance")
                
        elif provider == 'google':
            if 'gemini-2.5' in model_lower:
                if 'pro' in model_lower:
                    strengths.append("long context up to 1M+ tokens, multimodal, grounded responses")
                elif 'flash' in model_lower:
                    strengths.append("fast version optimized for speed")
            elif 'gemini-pro' in model_lower:
                if 'vision' in model_lower:
                    strengths.append("multimodal version with vision capabilities")
                else:
                    strengths.append("general purpose model with strong capabilities")
        
        # If no specific strengths found, generate generic one
        if not strengths:
            strengths.append("general purpose model")
        
        return ", ".join(strengths).capitalize()

    def _detect_model_capabilities(self, provider: str, model_id: str, api_model: Optional[Dict] = None) -> Dict[str, bool]:
        """Detect model capabilities for Python API usage (not web app features)."""
        
        model_lower = model_id.lower()
        capabilities = {
            'text_generation': True,  # All models can generate text
            'multimodal': False,
            'vision': False,
            'audio': False,
            'pdf_processing': False,  # Very limited in Python APIs
            'search': False,
            'reasoning': False,
            'coding': False,
        }
        
        # Vision/Multimodal detection - PYTHON API ONLY
        # GPT-4o Vision via Python API can accept image inputs
        if 'gpt-4o' in model_lower and provider == 'openai':
            capabilities['multimodal'] = True
            capabilities['vision'] = True
            # PDF processing is LIMITED in Python API - requires manual conversion to images
            capabilities['pdf_processing'] = False  # Not direct PDF support
        
        # Gemini Pro Vision via Python API
        elif ('gemini' in model_lower and 'vision' in model_lower) or 'gemini-pro-vision' in model_lower:
            capabilities['multimodal'] = True
            capabilities['vision'] = True
            capabilities['pdf_processing'] = False  # Not direct PDF support in Python API
        
        # Claude does NOT have vision in Python API (web app only)
        elif 'claude' in model_lower:
            capabilities['multimodal'] = False
            capabilities['vision'] = False
            capabilities['pdf_processing'] = False
        
        # Audio capabilities - PYTHON API ONLY
        # OpenAI has Whisper and TTS via separate API endpoints, not chat models
        # No current chat models support direct audio input/output via Python API
        capabilities['audio'] = False  # Chat models don't support audio directly
        
        # Search capabilities - PYTHON API ONLY
        # Most models don't have direct search capabilities via Python API
        # Grok might have some web access but this isn't well documented for Python API
        if 'grok' in model_lower:
            capabilities['search'] = True  # Grok claims real-time information
        else:
            capabilities['search'] = False
        
        # Reasoning capabilities - based on model architecture
        if any(term in model_lower for term in ['o1', 'reasoning']):
            capabilities['reasoning'] = True
        elif any(term in model_lower for term in ['gpt-4', 'claude-3', 'grok', 'gemini']):
            capabilities['reasoning'] = True  # Advanced models have good reasoning
        
        # Coding capabilities - based on actual Python API performance
        if any(term in model_lower for term in ['code', 'programming']):
            capabilities['coding'] = True
        elif any(term in model_lower for term in ['gpt-4', 'claude-3', 'o1', 'grok']):
            capabilities['coding'] = True  # Strong coding models
        
        # PDF processing - VERY LIMITED in Python APIs AND LOCAL LLMs
        # Python APIs generally require pre-processing PDFs to text
        # LOCAL LLMs (Ollama) have SAME limitations as Python APIs
        # NO models (hosted or local) have direct PDF input via Python API
        # Web apps have integrated PDF tools, but raw APIs and local models do not
        capabilities['pdf_processing'] = False  # Requires external PDF parsing
        
        return capabilities

    def _detect_local_model_capabilities(self, model_id: str) -> Dict[str, bool]:
        """Detect capabilities for local models based on their known strengths."""
        model_lower = model_id.lower()
        capabilities = {
            'text_generation': True,  # All models can generate text
            'multimodal': False,
            'vision': False,
            'audio': False,
            'pdf_processing': False,  # Requires external PDF parsing
            'search': False,  # Local models don't have web access
            'reasoning': False,
            'coding': False,
        }
        
        # Reasoning capabilities - based on model architecture and known performance
        if any(term in model_lower for term in ['deepseek-r1', 'qwq', 'llama-3.3', 'llama-3.1', 'qwen3', 'phi4', 'gemma3']):
            capabilities['reasoning'] = True  # Latest 2025 models with advanced reasoning
        elif any(term in model_lower for term in ['llama-3', 'llama-2', 'mistral', 'vicuna', 'wizardlm', 'orca']):
            capabilities['reasoning'] = True  # Older models with reasoning abilities
        
        # Coding capabilities - based on training and specialization
        if any(term in model_lower for term in ['coder', 'code', 'coding', 'programmer']):
            capabilities['coding'] = True  # Explicitly code-focused models
        elif any(term in model_lower for term in ['deepseek', 'qwen3', 'qwen2.5', 'llama-3', 'mistral', 'phi4']):
            capabilities['coding'] = True  # Models known for strong coding performance
        
        # Vision capabilities for local multimodal models
        if any(term in model_lower for term in ['vl', 'llava', 'vision', 'multimodal']):
            capabilities['multimodal'] = True
            capabilities['vision'] = True
        
        return capabilities

    def _build_local_model_info(self, model_id: str, tools_available: Dict, llama_cpp_available: bool, model_paths: Dict) -> Dict[str, Any]:
        """Build local model information."""
        specs = self.local_model_specs[model_id]
        pricing = self.pricing_info['local'][model_id]
        context_window = self.context_windows['local'][model_id]
        strengths = self.model_strengths['local'][model_id]
        
        # Dynamic capability detection for local models
        capabilities = self._detect_local_model_capabilities(model_id)
        
        # Check if actual model files are available
        model_key = model_id.split('-')[0]  # e.g., 'llama-3-8b' -> 'llama'
        available_files = model_paths.get(model_key, [])
        
        return {
            'id': model_id,
            'provider': 'local',
            'type': 'local',
            'pricing': pricing,
            'context_window': context_window,
            'strengths': strengths,
            'capabilities': capabilities,
            'cost_per_1m_tokens': {'input': 0, 'output': 0},
            'size_gb': specs['size_gb'],
            'speed_rating': specs['speed_rating'],
            'format': specs['format'],
            'tools_available': tools_available,
            'llama_cpp_available': llama_cpp_available,
            'estimated_ram_usage': f"{specs['size_gb'] * 1.2:.1f} GB",  # Include overhead
            'local_files_found': len(available_files),
            'file_paths': available_files[:3] if available_files else [],  # Show first 3 paths
            'installation_status': 'ready' if (tools_available.get('llama-cpp-python') or tools_available.get('ctransformers')) else 'tools_missing',
            'release_date': self._get_model_release_date('local', model_id)
        }

    def collect_all_models(self):
        """Dynamically collect models from all providers with real-time pricing and discovery."""
        print("🚀 Starting comprehensive dynamic model collection...")
        
        self.check_api_keys()
        
        # First, discover all available models
        print("🔍 Phase 1: Dynamic model discovery")
        discovered = self.discover_available_models()
        
        # Add metadata to the data structure
        self.models_data['pricing_info'] = {
            'last_updated': datetime.now().isoformat(),
            'cache_duration_seconds': self.cache_duration,
            'pricing_sources': ['real-time-api', 'openrouter', 'litellm', 'fallback'],
            'validation_enabled': True,
            'discovery_enabled': True,
            'discovered_counts': {provider: len(models) for provider, models in discovered.items()}
        }
        
        # Collect from each provider with dynamic discovery
        print("🔍 Phase 2: Enhanced model information collection")
        self.models_data['providers']['openai'] = self.get_openai_models()
        self.models_data['providers']['anthropic'] = self.get_anthropic_models()
        self.models_data['providers']['xai'] = self.get_xai_models()
        self.models_data['providers']['google'] = self.get_google_models()
        self.models_data['local_models'] = self.get_local_models()
        
        # Generate routing recommendations
        self.models_data['routing_recommendations'] = self._generate_routing_recommendations()
        
        return True

    def _generate_routing_recommendations(self) -> Dict[str, Any]:
        """Generate intelligent routing recommendations."""
        return {
            'task_based_routing': {
                'physics_stem': {
                    'primary': 'grok-4',
                    'fallback': 'claude-3-opus-20240229',
                    'local_option': 'mixtral-8x7b',
                    'reasoning': 'Grok-4 has strong STEM focus, Claude Opus for complex reasoning'
                },
                'code_generation': {
                    'primary': 'gpt-4o',
                    'fallback': 'claude-3-5-sonnet-20241022',
                    'local_option': 'code-llama-7b',
                    'reasoning': 'GPT-4o excellent for tools/functions, Claude 3.5 Sonnet for coding'
                },
                'long_context': {
                    'primary': 'gemini-2.5-pro',
                    'fallback': 'claude-3-opus-20240229',
                    'local_option': 'llama-3-8b',
                    'reasoning': 'Gemini 2.5 Pro supports up to 1M+ tokens'
                },
                'cost_sensitive': {
                    'primary': 'claude-3-haiku-20240307',
                    'fallback': 'gpt-3.5-turbo',
                    'local_option': 'phi-3-mini',
                    'reasoning': 'Cheapest hosted options, local models have no API costs'
                },
                'multimodal_vision': {
                    'primary': 'gpt-4o',
                    'fallback': 'gemini-pro-vision',
                    'local_option': 'llava-7b',
                    'reasoning': 'GPT-4o best multimodal, Gemini good alternative'
                },
                'fast_simple_tasks': {
                    'primary': 'gpt-3.5-turbo',
                    'fallback': 'claude-3-haiku-20240307',
                    'local_option': 'mistral-7b',
                    'reasoning': 'Speed optimized models for quick responses'
                }
            },
            'routing_criteria': {
                'token_thresholds': {
                    'short': {'max_tokens': 4000, 'recommend': ['gpt-3.5-turbo', 'claude-3-haiku-20240307', 'mistral-7b']},
                    'medium': {'max_tokens': 32000, 'recommend': ['gpt-4o', 'claude-3-sonnet-20240229', 'mixtral-8x7b']},
                    'long': {'max_tokens': 200000, 'recommend': ['claude-3-opus-20240229', 'gemini-2.5-pro', 'llama-3-8b']},
                    'ultra_long': {'max_tokens': 1000000, 'recommend': ['gemini-2.5-pro', 'gemini-2.5-flash']}
                },
                'cost_tiers': {
                    'free': {'models': ['phi-3-mini', 'mistral-7b', 'llama-3-8b'], 'note': 'Local models only'},
                    'budget': {'max_cost_per_1k': 1.0, 'models': ['claude-3-haiku-20240307', 'gpt-3.5-turbo']},
                    'standard': {'max_cost_per_1k': 5.0, 'models': ['claude-3-sonnet-20240229', 'gpt-4o-mini']},
                    'premium': {'models': ['gpt-4o', 'claude-3-opus-20240229', 'grok-4']}
                }
            }
        }

    def save_json(self, filename: str = 'available_models.json'):
        """Save collected data as JSON."""
        print(f"💾 Saving JSON to {filename}...")
        
        with open(filename, 'w') as f:
            json.dump(self.models_data, f, indent=2, default=str)
        
        print(f"✅ JSON saved successfully")

    def save_markdown(self, filename: str = 'available_models.md'):
        """Save collected data as formatted Markdown."""
        print(f"📝 Saving Markdown to {filename}...")
        
        md_content = f"""# Available AI Models - Complete Guide

*Last updated: {self.models_data['last_updated']}*

This document provides comprehensive information about available AI models from OpenAI, Anthropic, xAI, Google, and local LLMs, including pricing, capabilities, technical specifications, and intelligent routing recommendations.

## Quick Reference - Model Selection Guide

### By Task Type
- **Physics/STEM**: Grok-4 → Claude 3 Opus → Mixtral 8x7B (local)
- **Code Generation**: GPT-4o → Claude 3.5 Sonnet → Code Llama 7B (local)
- **Long Context (100K+ tokens)**: Gemini 2.5 Pro → Claude 3 Opus → Llama 3 8B (local)
- **Cost-Sensitive**: Claude 3 Haiku → GPT-3.5 Turbo → Phi-3 Mini (local)
- **Multimodal/Vision**: GPT-4o → Gemini Pro Vision → Local vision models
- **Fast Simple Tasks**: GPT-3.5 Turbo → Claude 3 Haiku → Mistral 7B (local)

"""
        
        # Hosted models section
        for provider, models in self.models_data['providers'].items():
            if not models:
                continue
                
            md_content += f"## {provider.upper()} (Hosted)\n\n"
            
            for model_id, info in models.items():
                md_content += f"### {model_id}\n\n"
                
                context_window = info.get('context_window', 'Unknown')
                if isinstance(context_window, int):
                    md_content += f"- **Context Window**: {context_window:,} tokens\n"
                else:
                    md_content += f"- **Context Window**: {context_window} tokens\n"
                
                pricing = info.get('pricing', {})
                if isinstance(pricing, dict):
                    input_price = pricing.get('input', 'Unknown')
                    output_price = pricing.get('output', 'Unknown')
                    md_content += f"- **Pricing**: ${input_price}/1K input tokens, ${output_price}/1K output tokens\n"
                
                pricing_per_1k = info.get('pricing', {})
                if isinstance(pricing_per_1k, dict):
                    input_cost = pricing_per_1k.get('input', 'Unknown')
                    output_cost = pricing_per_1k.get('output', 'Unknown')
                    if isinstance(input_cost, (int, float)) and isinstance(output_cost, (int, float)):
                        md_content += f"- **Cost per 1K tokens**: ${input_cost:.3f} input, ${output_cost:.3f} output\n"
                
                md_content += f"- **Strengths**: {info.get('strengths', 'General purpose model')}\n"
                
                # Show release date (from created timestamp or our data)
                if 'created' in info and info['created']:
                    created_date = datetime.fromtimestamp(info['created']).strftime('%Y-%m-%d') if isinstance(info['created'], (int, float)) else info['created']
                    md_content += f"- **Release Date**: {created_date}\n"
                elif 'release_date' in info and info['release_date'] != 'Unknown':
                    md_content += f"- **Release Date**: {info['release_date']}\n"
                
                md_content += "\n"
        
        # Local models section
        if self.models_data['local_models']:
            md_content += "## LOCAL MODELS (Apple Silicon Optimized)\n\n"
            
            for model_id, info in self.models_data['local_models'].items():
                md_content += f"### {model_id}\n\n"
                md_content += f"- **Size**: {info.get('size_gb', 'Unknown')} GB\n"
                md_content += f"- **Speed Rating**: {'⭐' * info.get('speed_rating', 1)} ({info.get('speed_rating', 1)}/5)\n"
                md_content += f"- **Format**: {info.get('format', 'Unknown')}\n"
                md_content += f"- **Context Window**: {info.get('context_window', 'Unknown'):,} tokens\n"
                md_content += f"- **RAM Usage**: ~{info.get('estimated_ram_usage', 'Unknown')}\n"
                md_content += f"- **Strengths**: {info.get('strengths', 'General purpose model')}\n"
                md_content += f"- **API Cost**: $0.00 (local inference only)\n"
                if 'release_date' in info and info['release_date'] != 'Unknown':
                    md_content += f"- **Release Date**: {info['release_date']}\n"
                md_content += "\n"
        
        # Routing recommendations
        routing = self.models_data.get('routing_recommendations', {})
        if routing:
            md_content += "## Intelligent Routing Recommendations\n\n"
            
            task_routing = routing.get('task_based_routing', {})
            for task, recommendation in task_routing.items():
                md_content += f"### {task.replace('_', ' ').title()}\n"
                md_content += f"- **Primary**: {recommendation.get('primary', 'N/A')}\n"
                md_content += f"- **Fallback**: {recommendation.get('fallback', 'N/A')}\n"
                md_content += f"- **Local Option**: {recommendation.get('local_option', 'N/A')}\n"
                md_content += f"- **Reasoning**: {recommendation.get('reasoning', 'N/A')}\n\n"
        
        # Cost comparison table
        md_content += "## Cost Comparison (per 1M tokens)\n\n"
        md_content += "| Model | Provider | Type | Input Cost | Output Cost | Context Window |\n"
        md_content += "|-------|----------|------|------------|-------------|----------------|\n"
        
        all_models = []
        
        # Add hosted models
        for provider, models in self.models_data['providers'].items():
            for model_id, info in models.items():
                pricing_per_1k = info.get('pricing', {})
                all_models.append({
                    'model': model_id,
                    'provider': provider,
                    'type': 'hosted',
                    'input_cost': pricing_per_1k.get('input', 0),
                    'output_cost': pricing_per_1k.get('output', 0),
                    'context_window': info.get('context_window', 0)
                })
        
        # Add local models
        for model_id, info in self.models_data['local_models'].items():
            all_models.append({
                'model': model_id,
                'provider': 'local',
                'type': 'local',
                'input_cost': 0,
                'output_cost': 0,
                'context_window': info.get('context_window', 0)
            })
        
        # Sort by input cost (local models first)
        all_models.sort(key=lambda x: (x['type'] != 'local', x['input_cost'] if isinstance(x['input_cost'], (int, float)) else float('inf')))
        
        for model in all_models:
            input_cost = f"${model['input_cost']:,.2f}" if isinstance(model['input_cost'], (int, float)) and model['input_cost'] > 0 else "$0.00"
            output_cost = f"${model['output_cost']:,.2f}" if isinstance(model['output_cost'], (int, float)) and model['output_cost'] > 0 else "$0.00"
            context_window = f"{model['context_window']:,}" if isinstance(model['context_window'], int) else str(model['context_window'])
            md_content += f"| {model['model']} | {model['provider']} | {model['type']} | {input_cost} | {output_cost} | {context_window} |\n"
        
        md_content += f"\n---\n*Generated by Enhanced GetAvailableModels.py - Including Grok-4 and Local LLMs*\n"
        
        with open(filename, 'w') as f:
            f.write(md_content)
        
        print(f"✅ Markdown saved successfully")

    def save_html_table(self, filename: str = 'available_models.html'):
        """Create an interactive HTML file with sortable table."""
        print(f"📄 Creating HTML file: {filename}...")
        
        # Collect all models for the table
        all_models = []
        
        # Add hosted models
        for provider, models in self.models_data['providers'].items():
            for model_id, info in models.items():
                pricing_per_1k = info.get('pricing', {})
                
                # Get release date
                release_date = 'Unknown'
                if 'created' in info and info['created']:
                    release_date = datetime.fromtimestamp(info['created']).strftime('%Y-%m-%d') if isinstance(info['created'], (int, float)) else str(info['created'])
                elif 'release_date' in info:
                    release_date = info['release_date']
                
                all_models.append({
                    'model': model_id,
                    'provider': provider,
                    'type': 'hosted',
                    'input_cost': pricing_per_1k.get('input', 0),
                    'output_cost': pricing_per_1k.get('output', 0),
                    'context_window': info.get('context_window', 'Unknown'),
                    'release_date': release_date,
                    'capabilities': info.get('capabilities', {}),
                    'strengths': info.get('strengths', 'General purpose model')
                })
        
        # Add local models
        for model_id, info in self.models_data.get('local_models', {}).items():
            all_models.append({
                'model': model_id,
                'provider': 'local',
                'type': 'local',
                'input_cost': 0,
                'output_cost': 0,
                'context_window': info.get('context_window', 'Unknown'),
                'release_date': info.get('release_date', 'Unknown'),
                'capabilities': info.get('capabilities', {'text_generation': True}),
                'strengths': info.get('strengths', 'Local inference model')
            })
        
        # Sort by input cost (local models first)
        all_models.sort(key=lambda x: (x['type'] != 'local', x['input_cost'] if isinstance(x['input_cost'], (int, float)) else float('inf')))
        
        # Calculate summary statistics
        total_models = len(all_models)
        hosted_models = len([m for m in all_models if m['type'] == 'hosted'])
        local_models = len([m for m in all_models if m['type'] == 'local'])
        provider_count = len(self.models_data['providers'])
        
        # Create HTML content
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Models Comparison - Interactive Table</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        .updated {{
            text-align: center;
            color: #666;
            font-style: italic;
            margin-bottom: 20px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #28a745;
            margin: 20px 0;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #34495e;
            color: white;
            cursor: pointer;
            user-select: none;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        th:hover {{
            background-color: #2c3e50;
        }}
        th::after {{
            content: ' ↕️';
            font-size: 10px;
        }}
        .local {{
            background-color: #d4edda;
        }}
        .budget {{
            background-color: #fff3cd;
        }}
        .premium {{
            background-color: #f8d7da;
        }}
        .model-name {{
            font-weight: bold;
            max-width: 250px;
            word-break: break-word;
        }}
        .capabilities {{
            max-width: 200px;
            font-size: 11px;
            text-align: center;
        }}
        .strengths {{
            max-width: 300px;
            font-size: 12px;
        }}
        .cost {{
            font-weight: bold;
            text-align: right;
        }}
        .context {{
            text-align: right;
        }}
        .legend {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Models Comparison - All Available Models</h1>
        <div class="updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <h3>📊 Complete Model Database: {total_models} Models</h3>
            <p><strong>📡 Hosted Models:</strong> {hosted_models} (from {provider_count} providers)</p>
            <p><strong>💻 Local Models:</strong> {local_models} (available for installation)</p>
            <p><em>This table shows all known AI models including those requiring API keys or local installation.</em></p>
        </div>
        
        <div class="legend">
            <strong>Color Legend:</strong>
            <span class="legend-item local">🟢 Local/Free ($0 API cost)</span>
            <span class="legend-item budget">🟡 Budget (<$1/1K tokens)</span>
            <span class="legend-item premium">🔴 Premium (>$5/1K tokens)</span>
        </div>
        
        <table id="modelTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Model</th>
                    <th onclick="sortTable(1)">Provider</th>
                    <th onclick="sortTable(2)">Input Cost (per 1K tokens)</th>
                    <th onclick="sortTable(3)">Output Cost (per 1K tokens)</th>
                    <th onclick="sortTable(4)">Context Window</th>
                    <th onclick="sortTable(5)">Release Date</th>
                    <th onclick="sortTable(6)">Capabilities</th>
                    <th onclick="sortTable(7)">Strengths</th>
                </tr>
            </thead>
            <tbody>
'''

        # Add table rows
        for model in all_models:
            # Convert costs from per-1M to per-1K tokens for display
            input_cost_per_1k = model['input_cost'] / 1000 if isinstance(model['input_cost'], (int, float)) else 0
            output_cost_per_1k = model['output_cost'] / 1000 if isinstance(model['output_cost'], (int, float)) else 0
            
            # Determine row class based on cost (now correctly per-1K)
            if model['type'] == 'local':
                row_class = 'local'
            elif input_cost_per_1k < 1.0:
                row_class = 'budget'
            elif input_cost_per_1k > 5.0:
                row_class = 'premium'
            else:
                row_class = ''
            
            input_cost = f"${input_cost_per_1k:.3f}" if input_cost_per_1k > 0 else "$0.000"
            output_cost = f"${output_cost_per_1k:.3f}" if output_cost_per_1k > 0 else "$0.000"
            context_window = f"{model['context_window']:,}" if isinstance(model['context_window'], int) else str(model['context_window'])
            
            # Format capabilities
            capabilities = model.get('capabilities', {})
            capability_icons = []
            if capabilities.get('multimodal'):
                capability_icons.append('🖼️ Vision')
            if capabilities.get('audio'):
                capability_icons.append('🎵 Audio')
            if capabilities.get('pdf_processing'):
                capability_icons.append('📄 PDF')
            if capabilities.get('search'):
                capability_icons.append('🔍 Search')
            if capabilities.get('reasoning'):
                capability_icons.append('🧠 Reasoning')
            if capabilities.get('coding'):
                capability_icons.append('💻 Code')
            
            capability_str = ', '.join(capability_icons) if capability_icons else '📝 Text'
            
            html_content += f'''                <tr class="{row_class}">
                    <td class="model-name">{model['model']}</td>
                    <td>{model['provider']}</td>
                    <td class="cost">{input_cost}</td>
                    <td class="cost">{output_cost}</td>
                    <td class="context">{context_window}</td>
                    <td class="release-date">{model.get('release_date', 'Unknown')}</td>
                    <td class="capabilities">{capability_str}</td>
                    <td class="strengths">{model['strengths']}</td>
                </tr>
'''

        html_content += '''            </tbody>
        </table>
        
        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
            <p>Generated by Enhanced GetAvailableModels.py - Including Grok-4 and Local LLMs</p>
            <p>Click column headers to sort • Costs are estimates and may change</p>
        </div>
    </div>

    <script>
        function sortTable(columnIndex) {
            const table = document.getElementById("modelTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            
            // Determine sort direction
            const currentDirection = table.getAttribute("data-sort-direction") || "asc";
            const newDirection = currentDirection === "asc" ? "desc" : "asc";
            table.setAttribute("data-sort-direction", newDirection);
            
            rows.sort((a, b) => {
                const aText = a.cells[columnIndex].textContent.trim();
                const bText = b.cells[columnIndex].textContent.trim();
                
                // Handle numeric columns (costs and context window)
                if (columnIndex >= 2 && columnIndex <= 4) {
                    const aNum = parseFloat(aText.replace(/[$,]/g, '')) || 0;
                    const bNum = parseFloat(bText.replace(/[$,]/g, '')) || 0;
                    
                    if (newDirection === "asc") {
                        return aNum - bNum;
                    } else {
                        return bNum - aNum;
                    }
                } else {
                    // Handle text columns
                    if (newDirection === "asc") {
                        return aText.localeCompare(bText);
                    } else {
                        return bText.localeCompare(aText);
                    }
                }
            });
            
            // Clear tbody and append sorted rows
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));
            
            // Update header indicators
            const headers = table.querySelectorAll("th");
            headers.forEach((header, index) => {
                if (index === columnIndex) {
                    header.style.backgroundColor = "#2c3e50";
                    header.textContent = header.textContent.replace(/ [↕️↑↓]/g, '') + (newDirection === "asc" ? " ↑" : " ↓");
                } else {
                    header.style.backgroundColor = "#34495e";
                    header.textContent = header.textContent.replace(/ [↕️↑↓]/g, '') + " ↕️";
                }
            });
        }
        
        // Initialize table
        document.addEventListener("DOMContentLoaded", function() {
            console.log("AI Models table loaded with sorting functionality");
        });
    </script>
</body>
</html>'''

        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML table saved successfully")
        
        # Auto-open the HTML file in the default browser
        try:
            import webbrowser
            file_path = os.path.abspath(filename)
            webbrowser.open(f'file://{file_path}')
            print(f"🌐 Opening {filename} in browser...")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
        
        return filename

    def create_intelligent_router(self, filename: str = 'IntelligentLLMRouter.py'):
        """Create an intelligent router class for model selection."""
        print(f"🧠 Creating intelligent router: {filename}...")
        
        router_code = '''#!/usr/bin/env python3
"""
IntelligentLLMRouter.py - Intelligent Model Selection Router

Automatically selects the best LLM for each task based on:
- Task type and complexity
- Token length requirements  
- Cost constraints
- Performance requirements
- Local vs hosted preferences

Generated by GetAvailableModels.py
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class IntelligentLLMRouter:
    def __init__(self, models_data_file: str = 'available_models.json'):
        """Initialize router with model data."""
        try:
            with open(models_data_file, 'r') as f:
                self.models_data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {models_data_file} not found. Using default configuration.")
            self.models_data = self._get_default_models()
        
        self.routing_rules = self.models_data.get('routing_recommendations', {})
        
    def route_request(self, 
                     prompt: str, 
                     task_type: Optional[str] = None,
                     max_cost_per_1k: Optional[float] = None,
                     prefer_local: bool = False,
                     require_multimodal: bool = False,
                     context_length_estimate: Optional[int] = None) -> Dict[str, Any]:
        """
        Route a request to the best available model.
        
        Args:
            prompt: The input prompt/query
            task_type: Optional explicit task type
            max_cost_per_1k: Maximum cost per 1K tokens
            prefer_local: Prefer local models when possible
            require_multimodal: Require vision/multimodal capabilities
            context_length_estimate: Estimated context length needed
            
        Returns:
            Dict with recommended model and routing reasoning
        """
        
        # Detect task type if not provided
        if not task_type:
            task_type = self._detect_task_type(prompt)
        
        # Estimate context length if not provided
        if not context_length_estimate:
            context_length_estimate = self._estimate_context_length(prompt)
        
        # Get routing recommendation
        recommendation = self._get_task_recommendation(task_type)
        
        # Apply constraints
        final_model = self._apply_constraints(
            recommendation, 
            max_cost_per_1k=max_cost_per_1k,
            prefer_local=prefer_local,
            require_multimodal=require_multimodal,
            context_length=context_length_estimate
        )
        
        return {
            'recommended_model': final_model,
            'detected_task_type': task_type,
            'estimated_context_length': context_length_estimate,
            'routing_reasoning': self._explain_choice(final_model, task_type, recommendation),
            'alternatives': self._get_alternatives(recommendation, final_model),
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_task_type(self, prompt: str) -> str:
        """Detect task type from prompt content."""
        prompt_lower = prompt.lower()
        
        # Physics/STEM detection
        physics_keywords = ['physics', 'thermodynamics', 'quantum', 'mechanics', 'energy', 'force', 'acceleration']
        if any(keyword in prompt_lower for keyword in physics_keywords):
            return 'physics_stem'
        
        # Code detection
        code_keywords = ['function', 'class', 'def ', 'import', 'return', 'if __name__', 'print(', 'console.log']
        if any(keyword in prompt_lower for keyword in code_keywords):
            return 'code_generation'
        
        # Multimodal detection
        multimodal_keywords = ['image', 'photo', 'picture', 'diagram', 'chart', 'visual', 'screenshot']
        if any(keyword in prompt_lower for keyword in multimodal_keywords):
            return 'multimodal_vision'
        
        # Long context detection (heuristic based on prompt length)
        if len(prompt) > 10000:
            return 'long_context'
        
        # Simple/fast task detection
        if len(prompt) < 200 and any(word in prompt_lower for word in ['what', 'how', 'when', 'where', 'why']):
            return 'fast_simple_tasks'
        
        return 'general_purpose'
    
    def _estimate_context_length(self, prompt: str) -> int:
        """Estimate context length needed (rough tokens = chars/4)."""
        return len(prompt) // 4
    
    def _get_task_recommendation(self, task_type: str) -> Dict[str, str]:
        """Get base recommendation for task type."""
        task_routing = self.routing_rules.get('task_based_routing', {})
        
        if task_type in task_routing:
            return task_routing[task_type]
        
        # Default recommendation
        return {
            'primary': 'gpt-4o',
            'fallback': 'claude-3-sonnet-20240229', 
            'local_option': 'llama-3-8b',
            'reasoning': 'General purpose task, using balanced models'
        }
    
    def _apply_constraints(self, 
                          recommendation: Dict[str, str],
                          max_cost_per_1k: Optional[float] = None,
                          prefer_local: bool = False,
                          require_multimodal: bool = False,
                          context_length: int = 0) -> str:
        """Apply constraints to select final model."""
        
        candidates = [
            recommendation.get('primary'),
            recommendation.get('fallback'),
            recommendation.get('local_option')
        ]
        
        # Filter out None values
        candidates = [c for c in candidates if c]
        
        if prefer_local:
            local_candidate = recommendation.get('local_option')
            if local_candidate and self._check_model_constraints(local_candidate, max_cost_per_1k, require_multimodal, context_length):
                return local_candidate
        
        if require_multimodal:
            multimodal_models = ['gpt-4o', 'gemini-pro-vision', 'grok-vision-beta']
            for model in multimodal_models:
                if model in candidates and self._check_model_constraints(model, max_cost_per_1k, require_multimodal, context_length):
                    return model
        
        # Check candidates in order
        for candidate in candidates:
            if self._check_model_constraints(candidate, max_cost_per_1k, require_multimodal, context_length):
                return candidate
        
        # Fallback to cheapest available model
        return 'gpt-3.5-turbo'
    
    def _check_model_constraints(self, 
                                model_id: str,
                                max_cost_per_1k: Optional[float] = None,
                                require_multimodal: bool = False,
                                context_length: int = 0) -> bool:
        """Check if model meets constraints."""
        
        # Find model info across all providers
        model_info = None
        for provider_models in self.models_data.get('providers', {}).values():
            if model_id in provider_models:
                model_info = provider_models[model_id]
                break
        
        if not model_info:
            # Check local models
            local_models = self.models_data.get('local_models', {})
            if model_id in local_models:
                model_info = local_models[model_id]
        
        if not model_info:
            return False
        
        # Check cost constraint
        if max_cost_per_1k is not None:
            pricing = model_info.get('pricing', {})
            input_cost = pricing.get('input', 0)
            if isinstance(input_cost, (int, float)) and input_cost > max_cost_per_1k:
                return False
        
        # Check context length
        model_context = model_info.get('context_window', 0)
        if isinstance(model_context, int) and context_length > model_context:
            return False
        
        # Check multimodal requirement
        if require_multimodal:
            multimodal_models = ['gpt-4o', 'gemini-pro-vision', 'grok-vision-beta']
            if model_id not in multimodal_models:
                return False
        
        return True
    
    def _explain_choice(self, chosen_model: str, task_type: str, recommendation: Dict[str, str]) -> str:
        """Explain why this model was chosen."""
        base_reasoning = recommendation.get('reasoning', 'Standard routing logic')
        return f"Selected {chosen_model} for {task_type} task. {base_reasoning}"
    
    def _get_alternatives(self, recommendation: Dict[str, str], chosen_model: str) -> List[str]:
        """Get alternative model options."""
        alternatives = []
        for key in ['primary', 'fallback', 'local_option']:
            model = recommendation.get(key)
            if model and model != chosen_model:
                alternatives.append(model)
        return alternatives
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Default model configuration if data file not available."""
        return {
            'routing_recommendations': {
                'task_based_routing': {
                    'physics_stem': {
                        'primary': 'grok-4',
                        'fallback': 'claude-3-opus-20240229',
                        'local_option': 'mixtral-8x7b',
                        'reasoning': 'STEM-focused models'
                    },
                    'code_generation': {
                        'primary': 'gpt-4o',
                        'fallback': 'claude-3-5-sonnet-20241022',
                        'local_option': 'code-llama-7b',
                        'reasoning': 'Code-optimized models'
                    },
                    'general_purpose': {
                        'primary': 'gpt-4o',
                        'fallback': 'claude-3-sonnet-20240229',
                        'local_option': 'llama-3-8b',
                        'reasoning': 'Balanced general purpose models'
                    }
                }
            }
        }

# Example usage
if __name__ == "__main__":
    router = IntelligentLLMRouter()
    
    # Example routing requests
    test_prompts = [
        ("Explain quantum mechanics and thermodynamics", None),
        ("Write a Python function to sort a list", None),
        ("What's the weather like?", None),
        ("def fibonacci(n):\\n    if n <= 1:\\n        return n", "code_generation")
    ]
    
    print("🧠 Intelligent LLM Router - Test Results")
    print("=" * 60)
    
    for prompt, task_type in test_prompts:
        result = router.route_request(prompt, task_type=task_type)
        print(f"\\nPrompt: {prompt[:50]}...")
        print(f"Recommended: {result['recommended_model']}")
        print(f"Task Type: {result['detected_task_type']}")
        print(f"Reasoning: {result['routing_reasoning']}")
'''
        
        with open(filename, 'w') as f:
            f.write(router_code)
        
        print(f"✅ Intelligent router created successfully")

    def create_current_models_files(self):
        """Create files for currently available models only (with API keys + installed local models)."""
        print("🔄 Creating current/available models subset files...")
        
        # Get currently available providers (with API keys)
        available_api_keys = {
            'openai': self.openai_api_key is not None,
            'anthropic': self.anthropic_api_key is not None, 
            'xai': self.xai_api_key is not None,
            'google': self.google_api_key is not None
        }
        
        # Get currently installed local models via Ollama
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            installed_local_models = set()
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        installed_local_models.add(model_name)
        except Exception:
            installed_local_models = set()
        
        # Filter data to only include currently available models
        current_data = {
            'last_updated': self.models_data['last_updated'],
            'providers': {},
            'local_models': {},
            'routing_recommendations': self.models_data.get('routing_recommendations', {}),
            'pricing_info': self.models_data.get('pricing_info', {})
        }
        
        # Add providers with API keys
        available_provider_count = 0
        for provider, has_key in available_api_keys.items():
            if has_key and provider in self.models_data['providers']:
                current_data['providers'][provider] = self.models_data['providers'][provider]
                available_provider_count += 1
        
        # Add only installed local models
        available_local_count = 0
        for model_id, model_data in self.models_data['local_models'].items():
            # Check if this model has an ollama_name field that matches installed models
            ollama_name = model_data.get('ollama_name')
            if ollama_name and ollama_name in installed_local_models:
                current_data['local_models'][model_id] = model_data
                available_local_count += 1
                continue
            
            # Fallback: Try to match by name patterns
            model_name_variations = [
                model_id.replace('-', ':'),
                model_id.replace('-', ''),
                model_id.replace('_', ':'),
                model_id.replace('_', ''),
                model_id + ':latest'
            ]
            
            for variation in model_name_variations:
                if variation in installed_local_models:
                    current_data['local_models'][model_id] = model_data
                    available_local_count += 1
                    break
        
        # Save current models JSON
        with open('available_models_current.json', 'w') as f:
            json.dump(current_data, f, indent=2, default=str)
        print("✅ Current models JSON saved")
        
        # Create current models markdown
        self.save_current_markdown(current_data, available_provider_count, available_local_count)
        
        # Create current models HTML
        self.save_current_html_table(current_data, available_provider_count, available_local_count)
        
        total_current = sum(len(models) for models in current_data['providers'].values()) + len(current_data['local_models'])
        print(f"✅ Current models subset created: {total_current} available models")
        print(f"   📡 Available hosted models: {sum(len(models) for models in current_data['providers'].values())}")
        print(f"   💻 Available local models: {len(current_data['local_models'])}")

    def save_current_markdown(self, current_data, available_provider_count, available_local_count):
        """Save current models as markdown file."""
        
        total_current_hosted = sum(len(models) for models in current_data['providers'].values())
        total_current_local = len(current_data['local_models'])
        total_current = total_current_hosted + total_current_local
        
        md_content = f"""# Currently Available AI Models - Practical Guide

*Last updated: {current_data['last_updated']}*

This document shows only the AI models **currently available to you** based on your API keys and installed local models.

## 🎯 Quick Summary

**Total Available Models: {total_current}**
- 📡 **Hosted Models**: {total_current_hosted} (from {available_provider_count} providers with API keys)
- 💻 **Local Models**: {total_current_local} (installed via Ollama)

## 🗝️ Available Providers

"""
        
        # Add provider status
        api_key_status = [
            ('OpenAI', 'openai' in current_data['providers'], 'GPT-4o, O1, ChatGPT models'),
            ('Anthropic', 'anthropic' in current_data['providers'], 'Claude 3.5 Sonnet, Opus, Haiku'),
            ('xAI', 'xai' in current_data['providers'], 'Grok-2, Grok-3, Grok-4 models'),
            ('Google', 'google' in current_data['providers'], 'Gemini 2.5 Pro, Flash models')
        ]
        
        for provider, available, description in api_key_status:
            status = "✅ Available" if available else "❌ No API key"
            md_content += f"- **{provider}**: {status}"
            if available:
                md_content += f" - {description}"
            md_content += "\\n"
        
        # Add local models status
        md_content += f"""
## 💻 Local Models (Ollama)

**Installed Models: {total_current_local}**

"""
        
        for model_id, model_data in current_data['local_models'].items():
            size_gb = model_data.get('size_gb', 'Unknown')
            speed = model_data.get('speed_rating', 0)
            stars = "⭐" * speed if speed > 0 else ""
            strengths = model_data.get('strengths', 'General purpose model')
            md_content += f"- **{model_id}**: {size_gb}GB {stars} - {strengths}\\n"
        
        # Add hosted models breakdown
        if current_data['providers']:
            md_content += f"""
## 📡 Hosted Models Breakdown

"""
            for provider, models in current_data['providers'].items():
                md_content += f"### {provider.title()} ({len(models)} models)\\n\\n"
                
                # Group models by cost tier
                budget_models = []
                standard_models = []
                premium_models = []
                
                for model_id, model_data in models.items():
                    input_cost = model_data.get('pricing', {}).get('input', 0)
                    if input_cost <= 1.0:
                        budget_models.append((model_id, model_data))
                    elif input_cost <= 5.0:
                        standard_models.append((model_id, model_data))
                    else:
                        premium_models.append((model_id, model_data))
                
                if budget_models:
                    md_content += "**Budget Models (<$1/1K tokens):**\\n"
                    for model_id, model_data in budget_models[:3]:  # Show top 3
                        cost = model_data.get('pricing', {}).get('input', 0)
                        md_content += f"- {model_id}: ${cost:.3f}/1K tokens\\n"
                    md_content += "\\n"
                
                if standard_models:
                    md_content += "**Standard Models ($1-5/1K tokens):**\\n"
                    for model_id, model_data in standard_models[:3]:  # Show top 3
                        cost = model_data.get('pricing', {}).get('input', 0)
                        md_content += f"- {model_id}: ${cost:.3f}/1K tokens\\n"
                    md_content += "\\n"
                
                if premium_models:
                    md_content += "**Premium Models (>$5/1K tokens):**\\n"
                    for model_id, model_data in premium_models[:3]:  # Show top 3
                        cost = model_data.get('pricing', {}).get('input', 0)
                        md_content += f"- {model_id}: ${cost:.3f}/1K tokens\\n"
                    md_content += "\\n"
        
        md_content += f"""
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
print(f"Recommended: {{result['recommended_model']}}")
```

## 📊 Cost Comparison (Available Models Only)

**Cheapest Options:**
"""
        
        # Find cheapest available models
        all_available_models = []
        for provider, models in current_data['providers'].items():
            for model_id, model_data in models.items():
                cost = model_data.get('pricing', {}).get('input', 0)
                all_available_models.append((cost, f"{provider}/{model_id}"))
        
        # Add local models (free)
        for model_id in current_data['local_models'].keys():
            all_available_models.append((0.0, f"local/{model_id}"))
        
        # Sort by cost and show cheapest
        all_available_models.sort()
        for i, (cost, model) in enumerate(all_available_models[:8]):
            if cost == 0:
                md_content += f"{i+1}. **{model}**: Free (local)\\n"
            else:
                md_content += f"{i+1}. **{model}**: ${cost:.3f}/1K tokens\\n"
        
        md_content += f"""

*This file shows only models you can use immediately. For complete model information, see `available_models.md`.*
"""
        
        with open('available_models_current.md', 'w') as f:
            f.write(md_content)
        
        print("✅ Current models markdown saved")

    def save_current_html_table(self, current_data, available_provider_count, available_local_count):
        """Save current models as interactive HTML table."""
        
        total_current_hosted = sum(len(models) for models in current_data['providers'].values())
        total_current_local = len(current_data['local_models'])
        total_current = total_current_hosted + total_current_local
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Currently Available AI Models</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .updated {{ font-size: 0.9em; opacity: 0.8; margin-top: 10px; }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #28a745;
            margin: 20px;
            border-radius: 5px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: #f1f3f4;
            flex-wrap: wrap;
        }}
        .legend-item {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .legend-item.local {{ background: #d4edda; color: #155724; }}
        .legend-item.budget {{ background: #fff3cd; color: #856404; }}
        .legend-item.premium {{ background: #f8d7da; color: #721c24; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #34495e;
            color: white;
            cursor: pointer;
            user-select: none;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        th:hover {{ background: #2c3e50; }}
        tr:hover {{ background: #f5f5f5; }}
        .local-row {{ background: #d4edda !important; }}
        .budget-row {{ background: #fff3cd !important; }}
        .premium-row {{ background: #f8d7da !important; }}
        .cost {{ font-weight: bold; }}
        .model-name {{ font-weight: bold; color: #2c3e50; }}
        .provider {{ 
            text-transform: uppercase;
            font-size: 0.8em;
            color: #666;
            font-weight: bold;
        }}
        .context {{ color: #28a745; font-weight: bold; }}
        .strengths {{ font-size: 0.9em; color: #555; }}
        .capabilities {{
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}
        .capability {{
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Currently Available AI Models</h1>
            <div class="updated">Last updated: {current_data['last_updated']}</div>
        </div>
        
        <div class="summary">
            <h3>🚀 Ready to Use: {total_current} Models</h3>
            <p><strong>📡 Hosted Models:</strong> {total_current_hosted} (from {available_provider_count} providers with API keys)</p>
            <p><strong>💻 Local Models:</strong> {total_current_local} (installed via Ollama)</p>
            <p><em>This table shows only models you can use immediately with your current setup.</em></p>
        </div>
        
        <div class="legend">
            <strong>Color Legend:</strong>
            <span class="legend-item local">🟢 Local/Free ($0 API cost)</span>
            <span class="legend-item budget">🟡 Budget (<$1/1K tokens)</span>
            <span class="legend-item premium">🔴 Premium (>$5/1K tokens)</span>
        </div>
        
        <table id="modelsTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)" style="cursor: pointer;">Model ID ↕️</th>
                    <th onclick="sortTable(1)" style="cursor: pointer;">Provider ↕️</th>
                    <th onclick="sortTable(2)" style="cursor: pointer;">Input Cost (per 1K tokens) ↕️</th>
                    <th onclick="sortTable(3)" style="cursor: pointer;">Output Cost (per 1K tokens) ↕️</th>
                    <th onclick="sortTable(4)" style="cursor: pointer;">Context Window ↕️</th>
                    <th onclick="sortTable(5)" style="cursor: pointer;">Release Date ↕️</th>
                    <th onclick="sortTable(6)" style="cursor: pointer;">Strengths ↕️</th>
                    <th onclick="sortTable(7)" style="cursor: pointer;">Capabilities ↕️</th>
                </tr>
            </thead>
            <tbody>
'''
        
        # Add table rows for all available models
        all_rows = []
        
        # Add local models
        for model_id, model_data in current_data['local_models'].items():
            context_window = model_data.get('context_window', 'Unknown')
            strengths = model_data.get('strengths', 'General purpose model')
            capabilities = model_data.get('capabilities', {})
            
            # Create capabilities badges
            cap_badges = []
            for cap, enabled in capabilities.items():
                if enabled:
                    cap_badges.append(f'<span class="capability">{cap.replace("_", " ").title()}</span>')
            cap_html = ''.join(cap_badges) if cap_badges else '<span class="capability">Text Generation</span>'
            
            row_class = "local-row"
            release_date = model_data.get('release_date', 'Unknown')
            all_rows.append((
                f'<tr class="{row_class}">',
                f'<td class="model-name">{model_id}</td>',
                f'<td class="provider">LOCAL</td>',
                f'<td class="cost">$0.000</td>',
                f'<td class="cost">$0.000</td>',
                f'<td class="context">{context_window:,} tokens</td>',
                f'<td class="release-date">{release_date}</td>',
                f'<td class="strengths">{strengths}</td>',
                f'<td class="capabilities">{cap_html}</td>',
                '</tr>'
            ))
        
        # Add hosted models
        for provider, models in current_data['providers'].items():
            for model_id, model_data in models.items():
                pricing = model_data.get('pricing', {})
                input_cost = pricing.get('input', 0)
                output_cost = pricing.get('output', 0)
                context_window = model_data.get('context_window', 0)
                strengths = model_data.get('strengths', 'General purpose model')
                capabilities = model_data.get('capabilities', {})
                
                # Convert cost from per-1M to per-1K for classification
                input_cost_per_1k = input_cost / 1000 if input_cost > 0 else 0
                output_cost_per_1k = output_cost / 1000 if output_cost > 0 else 0
                
                # Determine row class based on cost (per-1K)
                if input_cost_per_1k <= 1.0:
                    row_class = "budget-row"
                elif input_cost_per_1k > 5.0:
                    row_class = "premium-row"
                else:
                    row_class = ""
                
                # Create capabilities badges
                cap_badges = []
                for cap, enabled in capabilities.items():
                    if enabled:
                        cap_badges.append(f'<span class="capability">{cap.replace("_", " ").title()}</span>')
                cap_html = ''.join(cap_badges) if cap_badges else '<span class="capability">Text Generation</span>'
                
                context_display = f"{context_window:,} tokens" if context_window > 0 else "Unknown"
                
                # Get release date
                release_date = 'Unknown'
                if 'created' in model_data and model_data['created']:
                    release_date = datetime.fromtimestamp(model_data['created']).strftime('%Y-%m-%d') if isinstance(model_data['created'], (int, float)) else str(model_data['created'])
                elif 'release_date' in model_data:
                    release_date = model_data['release_date']
                
                all_rows.append((
                    f'<tr class="{row_class}">',
                    f'<td class="model-name">{model_id}</td>',
                    f'<td class="provider">{provider.upper()}</td>',
                    f'<td class="cost">${input_cost_per_1k:.3f}</td>',
                    f'<td class="cost">${output_cost_per_1k:.3f}</td>',
                    f'<td class="context">{context_display}</td>',
                    f'<td class="release-date">{release_date}</td>',
                    f'<td class="strengths">{strengths}</td>',
                    f'<td class="capabilities">{cap_html}</td>',
                    '</tr>'
                ))
        
        # Add all rows to HTML
        for row_parts in all_rows:
            html_content += ''.join(row_parts) + '\\n'
        
        html_content += '''
            </tbody>
        </table>
    </div>
    
    <script>
        let sortDirection = {};
        
        function sortTable(columnIndex) {
            const table = document.getElementById("modelsTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));
            
            // Determine sort direction
            const currentDirection = sortDirection[columnIndex] || "asc";
            const newDirection = currentDirection === "asc" ? "desc" : "asc";
            sortDirection[columnIndex] = newDirection;
            
            // Sort rows
            rows.sort((a, b) => {
                const aText = a.cells[columnIndex].textContent.trim();
                const bText = b.cells[columnIndex].textContent.trim();
                
                // Handle numeric columns (cost, context window)
                if (columnIndex === 2 || columnIndex === 3) { // Cost columns
                    const aNum = parseFloat(aText.replace(/[$,]/g, ''));
                    const bNum = parseFloat(bText.replace(/[$,]/g, ''));
                    return newDirection === "asc" ? aNum - bNum : bNum - aNum;
                } else if (columnIndex === 4) { // Context window
                    const aNum = parseInt(aText.replace(/[^0-9]/g, '')) || 0;
                    const bNum = parseInt(bText.replace(/[^0-9]/g, '')) || 0;
                    return newDirection === "asc" ? aNum - bNum : bNum - aNum;
                } else {
                    // Text columns
                    return newDirection === "asc" ? 
                        aText.localeCompare(bText) : 
                        bText.localeCompare(aText);
                }
            });
            
            // Clear and re-add rows
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));
            
            // Update header indicators
            const headers = table.querySelectorAll("th");
            headers.forEach((header, index) => {
                if (index === columnIndex) {
                    header.style.backgroundColor = "#2c3e50";
                    header.textContent = header.textContent.replace(/ [↕️↑↓]/g, '') + (newDirection === "asc" ? " ↑" : " ↓");
                } else {
                    header.style.backgroundColor = "#34495e";
                    header.textContent = header.textContent.replace(/ [↕️↑↓]/g, '') + " ↕️";
                }
            });
        }
        
        // Initialize table
        document.addEventListener("DOMContentLoaded", function() {
            console.log("Currently available AI models table loaded");
        });
    </script>
</body>
</html>'''
        
        with open('available_models_current.html', 'w') as f:
            f.write(html_content)
        
        print("✅ Current models HTML saved")
        
        # Auto-open the current models HTML file
        try:
            import webbrowser
            file_path = os.path.abspath('available_models_current.html')
            webbrowser.open(f'file://{file_path}')
            print("🌐 Opening available_models_current.html in browser...")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")

    def run(self):
        """Main execution method."""
        print("🎯 Enhanced AI Model Information Collector & Router")
        print("=" * 60)
        
        if self.collect_all_models():
            self.save_json()
            self.save_markdown()
            self.save_html_table()
            self.create_intelligent_router()
            
            # Create current/available models subset
            self.create_current_models_files()
            
            total_hosted = sum(len(models) for models in self.models_data['providers'].values())
            total_local = len(self.models_data['local_models'])
            total_models = total_hosted + total_local
            
            print(f"\n🎉 Successfully collected information for {total_models} models")
            print(f"   📡 Hosted models: {total_hosted}")
            print(f"   💻 Local models: {total_local}")
            print("📄 Files generated:")
            print("   - available_models.json")
            print("   - available_models.md")
            print("   - available_models.html")
            print("   - available_models_current.json")
            print("   - available_models_current.md") 
            print("   - available_models_current.html")
            print("   - IntelligentLLMRouter.py")
        else:
            print("❌ Model collection failed")
            sys.exit(1)

if __name__ == "__main__":
    collector = EnhancedModelInfoCollector()
    collector.run()