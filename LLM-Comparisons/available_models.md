# Available AI Models - Complete Guide

*Last updated: 2025-07-31T08:51:18.905658*

This document provides comprehensive information about available AI models from OpenAI, Anthropic, xAI, Google, and local LLMs, including pricing, capabilities, technical specifications, and intelligent routing recommendations.

## Quick Reference - Model Selection Guide

### By Task Type
- **Physics/STEM**: Grok-4 → Claude 3 Opus → Mixtral 8x7B (local)
- **Code Generation**: GPT-4o → Claude 3.5 Sonnet → Code Llama 7B (local)
- **Long Context (100K+ tokens)**: Gemini 2.5 Pro → Claude 3 Opus → Llama 3 8B (local)
- **Cost-Sensitive**: Claude 3 Haiku → GPT-3.5 Turbo → Phi-3 Mini (local)
- **Multimodal/Vision**: GPT-4o → Gemini Pro Vision → Local vision models
- **Fast Simple Tasks**: GPT-3.5 Turbo → Claude 3 Haiku → Mistral 7B (local)

## OPENAI (Hosted)

### gpt-4-0613

- **Context Window**: 8,192 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2023-06-12

### gpt-4

- **Context Window**: 8,192 tokens
- **Pricing**: $0.030000000000000002/1K input tokens, $0.060000000000000005/1K output tokens
- **Cost per 1K tokens**: $0.030 input, $0.060 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2023-06-27

### gpt-3.5-turbo

- **Context Window**: 16,385 tokens
- **Pricing**: $0.0005/1K input tokens, $0.0015/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.002 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2023-02-28

### gpt-4o-realtime-preview-2025-06-03

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-06-02

### gpt-4o-audio-preview-2025-06-03

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-06-02

### gpt-3.5-turbo-instruct

- **Context Window**: 16,385 tokens
- **Pricing**: $0.0015/1K input tokens, $0.002/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.002 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2023-08-24

### gpt-3.5-turbo-instruct-0914

- **Context Window**: 16,385 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2023-09-07

### gpt-4-1106-preview

- **Context Window**: 8,192 tokens
- **Pricing**: $0.01/1K input tokens, $0.030000000000000002/1K output tokens
- **Cost per 1K tokens**: $0.010 input, $0.030 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2023-11-02

### gpt-3.5-turbo-1106

- **Context Window**: 16,385 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2023-11-02

### gpt-4-0125-preview

- **Context Window**: 8,192 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2024-01-23

### gpt-4-turbo-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.01/1K input tokens, $0.030000000000000002/1K output tokens
- **Cost per 1K tokens**: $0.010 input, $0.030 output
- **Strengths**: Advanced reasoning with large context window
- **Release Date**: 2024-01-23

### gpt-3.5-turbo-0125

- **Context Window**: 16,385 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2024-01-23

### gpt-4-turbo

- **Context Window**: 128,000 tokens
- **Pricing**: $0.01/1K input tokens, $0.030000000000000002/1K output tokens
- **Cost per 1K tokens**: $0.010 input, $0.030 output
- **Strengths**: Advanced reasoning with large context window
- **Release Date**: 2024-04-05

### gpt-4-turbo-2024-04-09

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Advanced reasoning with large context window
- **Release Date**: 2024-04-08

### gpt-4o

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0025/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.010 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-05-10

### gpt-4o-2024-05-13

- **Context Window**: 128,000 tokens
- **Pricing**: $0.005/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.005 input, $0.015 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-05-10

### gpt-4o-mini-2024-07-18

- **Context Window**: 128,000 tokens
- **Pricing**: $0.00015/1K input tokens, $0.0006/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.001 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-07-16

### gpt-4o-mini

- **Context Window**: 128,000 tokens
- **Pricing**: $0.00015/1K input tokens, $0.0006/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.001 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-07-16

### gpt-4o-2024-08-06

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0025/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.010 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-08-04

### chatgpt-4o-latest

- **Context Window**: 128,000 tokens
- **Pricing**: $0.005/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.005 input, $0.015 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-08-12

### o1-mini-2024-09-12

- **Context Window**: 200,000 tokens
- **Pricing**: $0.0011/1K input tokens, $0.0044/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.004 output
- **Strengths**: Reasoning-focused model optimized for coding and math
- **Release Date**: 2024-09-06

### o1-mini

- **Context Window**: 200,000 tokens
- **Pricing**: $0.0011/1K input tokens, $0.0044/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.004 output
- **Strengths**: Reasoning-focused model optimized for coding and math
- **Release Date**: 2024-09-06

### gpt-4o-realtime-preview-2024-10-01

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-09-23

### gpt-4o-audio-preview-2024-10-01

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-09-26

### gpt-4o-audio-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-09-27

### gpt-4o-realtime-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-09-29

### gpt-4o-realtime-preview-2024-12-17

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-11

### gpt-4o-audio-preview-2024-12-17

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-12

### gpt-4o-mini-realtime-preview-2024-12-17

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-13

### gpt-4o-mini-audio-preview-2024-12-17

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-13

### o1-2024-12-17

- **Context Window**: 200,000 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Sophisticated reasoning capabilities
- **Release Date**: 2024-12-15

### o1

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.060000000000000005/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.060 output
- **Strengths**: Sophisticated reasoning capabilities
- **Release Date**: 2024-12-16

### gpt-4o-mini-realtime-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-16

### gpt-4o-mini-audio-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio processing and real-time interaction, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2024-12-16

### gpt-4o-2024-11-20

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0025/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.010 output
- **Strengths**: Latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-02-11

### gpt-4o-search-preview-2025-03-11

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Web search integration, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-07

### gpt-4o-search-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0025/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.010 output
- **Strengths**: Web search integration, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-07

### gpt-4o-mini-search-preview-2025-03-11

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Web search integration, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-07

### gpt-4o-mini-search-preview

- **Context Window**: 128,000 tokens
- **Pricing**: $0.00015/1K input tokens, $0.0006/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.001 output
- **Strengths**: Web search integration, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-07

### gpt-4o-transcribe

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio transcription, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-15

### gpt-4o-mini-transcribe

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Audio transcription, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-15

### o1-pro-2025-03-19

- **Context Window**: 200,000 tokens
- **Pricing**: $0.00125/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.010 output
- **Strengths**: Advanced reasoning for complex problem-solving
- **Release Date**: 2025-03-17

### o1-pro

- **Context Window**: 200,000 tokens
- **Pricing**: $0.15/1K input tokens, $0.6/1K output tokens
- **Cost per 1K tokens**: $0.150 input, $0.600 output
- **Strengths**: Advanced reasoning for complex problem-solving
- **Release Date**: 2025-03-17

### gpt-4o-mini-tts

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Text-to-speech generation, latest multimodal model, excellent for complex reasoning
- **Release Date**: 2025-03-19

### gpt-4.1-2025-04-14

- **Context Window**: 8,192 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-4.1

- **Context Window**: 8,192 tokens
- **Pricing**: $0.002/1K input tokens, $0.008/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.008 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-4.1-mini-2025-04-14

- **Context Window**: 8,192 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-4.1-mini

- **Context Window**: 8,192 tokens
- **Pricing**: $0.00039999999999999996/1K input tokens, $0.0015999999999999999/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.002 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-4.1-nano-2025-04-14

- **Context Window**: 8,192 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-4.1-nano

- **Context Window**: 8,192 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Strong reasoning and creative tasks
- **Release Date**: 2025-04-10

### gpt-3.5-turbo-16k

- **Context Window**: 16,384 tokens
- **Pricing**: $0.003/1K input tokens, $0.004/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.004 output
- **Strengths**: Fast and cost-effective for simpler tasks
- **Release Date**: 2023-05-10

## ANTHROPIC (Hosted)

### claude-opus-4-20250514

- **Context Window**: 128,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: General purpose model

### claude-sonnet-4-20250514

- **Context Window**: 128,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: General purpose model

### claude-3-7-sonnet-20250219

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: General purpose model

### claude-3-5-sonnet-20241022

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: Latest claude with excellent coding and analysis capabilities

### claude-3-5-haiku-20241022

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: Latest claude with excellent coding and analysis capabilities

### claude-3-5-sonnet-20240620

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: Latest claude with excellent coding and analysis capabilities

### claude-3-haiku-20240307

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: Fastest claude model, good for simple tasks and high volume

### claude-3-opus-20240229

- **Context Window**: 200,000 tokens
- **Pricing**: $0.015000000000000001/1K input tokens, $0.075/1K output tokens
- **Cost per 1K tokens**: $0.015 input, $0.075 output
- **Strengths**: Most capable claude model for complex reasoning tasks

## XAI (Hosted)

### grok-2-1212

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.010 output
- **Strengths**: Balanced reasoning and performance
- **Release Date**: 2025-01-19

### grok-2-vision-1212

- **Context Window**: 128,000 tokens
- **Pricing**: $0.002/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.002 input, $0.010 output
- **Strengths**: Multimodal vision capabilities, balanced reasoning and performance
- **Release Date**: 2024-12-11

### grok-3

- **Context Window**: 128,000 tokens
- **Pricing**: $0.003/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.015 output
- **Strengths**: Advanced reasoning capabilities
- **Release Date**: 2025-04-03

### grok-3-fast

- **Context Window**: 128,000 tokens
- **Pricing**: $0.003/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.015 output
- **Strengths**: Optimized for speed and quick responses
- **Release Date**: 2025-04-03

### grok-3-mini

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0003/1K input tokens, $0.0005/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.001 output
- **Strengths**: Compact model for efficient processing
- **Release Date**: 2025-04-03

### grok-3-mini-fast

- **Context Window**: 128,000 tokens
- **Pricing**: $0.003/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.015 output
- **Strengths**: Compact model for efficient processing
- **Release Date**: 2025-04-03

### grok-4-0709

- **Context Window**: 128,000 tokens
- **Pricing**: $0.003/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.015 output
- **Strengths**: Stem and science focused, strong reasoning
- **Release Date**: 2025-07-08

### grok-2-image-1212

- **Context Window**: 128,000 tokens
- **Pricing**: $0.003/1K input tokens, $0.015000000000000001/1K output tokens
- **Cost per 1K tokens**: $0.003 input, $0.015 output
- **Strengths**: Multimodal vision capabilities, balanced reasoning and performance
- **Release Date**: 2025-01-12

## GOOGLE (Hosted)

### gemini-2.5-pro

- **Context Window**: 1,000,000 tokens
- **Pricing**: $0.00125/1K input tokens, $0.01/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.010 output
- **Strengths**: Long context up to 1m+ tokens, multimodal, grounded responses
- **Release Date**: 2024-12-11

### gemini-2.5-flash

- **Context Window**: 1,000,000 tokens
- **Pricing**: $0.0003/1K input tokens, $0.0025/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.003 output
- **Strengths**: Fast version optimized for speed
- **Release Date**: 2024-12-11

### gemini-pro

- **Context Window**: 128,000 tokens
- **Pricing**: $0.00125/1K input tokens, $0.005/1K output tokens
- **Cost per 1K tokens**: $0.001 input, $0.005 output
- **Strengths**: General purpose model with strong capabilities
- **Release Date**: 2023-12-06

### gemini-pro-vision

- **Context Window**: 128,000 tokens
- **Pricing**: $0.0/1K input tokens, $0.0/1K output tokens
- **Cost per 1K tokens**: $0.000 input, $0.000 output
- **Strengths**: Multimodal vision capabilities, multimodal version with vision capabilities
- **Release Date**: 2023-12-06

## LOCAL MODELS (Apple Silicon Optimized)

### codellama-34b

- **Size**: 17.74360340554267 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~21.3 GB
- **Strengths**: Reliable general-purpose model optimized for Apple Silicon
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### qwen2-5-coder-32b

- **Size**: 18.488010296598077 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~22.2 GB
- **Strengths**: Specialized for code generation and programming tasks
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### mixtral-8x7b

- **Size**: 24.627523977309465 GB
- **Speed Rating**: ⭐⭐ (2/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~29.6 GB
- **Strengths**: General-purpose language model
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### deepseek-r1-32b

- **Size**: 18.487999037839472 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~22.2 GB
- **Strengths**: Advanced reasoning and chain-of-thought capabilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-20

### qwen2-5-32b

- **Size**: 18.488010083325207 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~22.2 GB
- **Strengths**: General-purpose language model
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### llama3-3-70b

- **Size**: 39.60022136196494 GB
- **Speed Rating**: ⭐⭐ (2/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~47.5 GB
- **Strengths**: Reliable general-purpose model optimized for Apple Silicon
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### qwen2-5-coder-1-5b

- **Size**: 0.9183418834581971 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~1.1 GB
- **Strengths**: Specialized for code generation and programming tasks
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### gemma2-9b

- **Size**: 5.069330723024905 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~6.1 GB
- **Strengths**: Google's safe and efficient language model
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### qwen2-5-7b

- **Size**: 4.361464951187372 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~5.2 GB
- **Strengths**: General-purpose language model
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### qwen2-5-coder-7b

- **Size**: 4.361465164460242 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~5.2 GB
- **Strengths**: Specialized for code generation and programming tasks
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### deepseek-r1-8b

- **Size**: 4.866510673426092 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~5.8 GB
- **Strengths**: Advanced reasoning and chain-of-thought capabilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-20

### phi3-mini

- **Size**: 2.0267245480790734 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~2.4 GB
- **Strengths**: Microsoft's compact model with strong reasoning
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### codellama-7b

- **Size**: 3.56315696798265 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~4.3 GB
- **Strengths**: Reliable general-purpose model optimized for Apple Silicon
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### mistral-7b

- **Size**: 4.072510063648224 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~4.9 GB
- **Strengths**: Excellent multilingual capabilities and efficiency
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### llama3-1-8b

- **Size**: 4.582808658480644 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~5.5 GB
- **Strengths**: Reliable general-purpose model optimized for Apple Silicon
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### qwen3-8b

- **Size**: 5.2 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~6.2 GB
- **Strengths**: Latest generation multilingual model with excellent performance; Latest Qwen generation
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-20

### qwen2-5vl-7b

- **Size**: 6.0 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 65,536 tokens
- **RAM Usage**: ~7.2 GB
- **Strengths**: Multimodal vision-language understanding; Vision-language model
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-01-01

### llama-3.3-70b

- **Size**: 43 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~51.6 GB
- **Strengths**: GPT-4 class performance, excellent reasoning and instruction following
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-06

### deepseek-r1-7b

- **Size**: 4.7 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 65,536 tokens
- **RAM Usage**: ~5.6 GB
- **Strengths**: Efficient reasoning model with strong problem-solving capabilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-20

### qwen3-14b

- **Size**: 9.0 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~10.8 GB
- **Strengths**: Larger Qwen3 model with enhanced reasoning and coding abilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-13

### qwen3-32b

- **Size**: 20 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~24.0 GB
- **Strengths**: High-performance Qwen3 model for complex tasks and reasoning
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-13

### qwen2.5-coder-7b

- **Size**: 4.7 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~5.6 GB
- **Strengths**: State-of-the-art code generation, competitive with GPT-4 for coding
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-11-11

### qwen2.5-coder-14b

- **Size**: 9.0 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~10.8 GB
- **Strengths**: Enhanced coding model with superior debugging and refactoring
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-11-11

### qwen2.5-coder-32b

- **Size**: 20 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~24.0 GB
- **Strengths**: Premium coding assistant, handles complex codebases and architecture
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-11-11

### qwen2.5-vl-7b

- **Size**: 6.0 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 65,536 tokens
- **RAM Usage**: ~7.2 GB
- **Strengths**: Multimodal model with vision understanding and reasoning
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-28

### qwen2.5-vl-32b

- **Size**: 21 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 65,536 tokens
- **RAM Usage**: ~25.2 GB
- **Strengths**: Advanced vision-language model with tool use capabilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-28

### llava-13b

- **Size**: 8.0 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 32,768 tokens
- **RAM Usage**: ~9.6 GB
- **Strengths**: Open-source vision model, good for image analysis and description
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-07-15

### qwq-32b

- **Size**: 20 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~24.0 GB
- **Strengths**: Specialized reasoning model with enhanced logical thinking
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-11-27

### llama-3.1-8b

- **Size**: 5.0 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~6.0 GB
- **Strengths**: Reliable general purpose model, well-optimized for Apple Silicon
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-07-23

### llama-3.1-70b

- **Size**: 43 GB
- **Speed Rating**: ⭐⭐⭐ (3/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~51.6 GB
- **Strengths**: High-performance Llama model for complex reasoning tasks
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-07-23

### gemma3-9b

- **Size**: 5.5 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~6.6 GB
- **Strengths**: Latest Gemma with improved safety and multilingual support
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-11

### phi4-14b

- **Size**: 9.1 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~10.9 GB
- **Strengths**: Microsoft's latest small language model with strong reasoning
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-11

### qwen3-1.7b

- **Size**: 1.2 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~1.4 GB
- **Strengths**: Ultra-lightweight model for basic tasks and edge deployment
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2025-01-13

### gemma3-4b

- **Size**: 2.5 GB
- **Speed Rating**: ⭐⭐⭐⭐⭐ (5/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~3.0 GB
- **Strengths**: Compact model with good performance-to-size ratio
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-12-11

### mistral-nemo-12b

- **Size**: 7.5 GB
- **Speed Rating**: ⭐⭐⭐⭐ (4/5)
- **Format**: GGUF (Q4_K_M)
- **Context Window**: 131,072 tokens
- **RAM Usage**: ~9.0 GB
- **Strengths**: Balanced model with strong multilingual capabilities
- **API Cost**: $0.00 (local inference only)
- **Release Date**: 2024-07-18

## Intelligent Routing Recommendations

### Physics Stem
- **Primary**: grok-4
- **Fallback**: claude-3-opus-20240229
- **Local Option**: mixtral-8x7b
- **Reasoning**: Grok-4 has strong STEM focus, Claude Opus for complex reasoning

### Code Generation
- **Primary**: gpt-4o
- **Fallback**: claude-3-5-sonnet-20241022
- **Local Option**: code-llama-7b
- **Reasoning**: GPT-4o excellent for tools/functions, Claude 3.5 Sonnet for coding

### Long Context
- **Primary**: gemini-2.5-pro
- **Fallback**: claude-3-opus-20240229
- **Local Option**: llama-3-8b
- **Reasoning**: Gemini 2.5 Pro supports up to 1M+ tokens

### Cost Sensitive
- **Primary**: claude-3-haiku-20240307
- **Fallback**: gpt-3.5-turbo
- **Local Option**: phi-3-mini
- **Reasoning**: Cheapest hosted options, local models have no API costs

### Multimodal Vision
- **Primary**: gpt-4o
- **Fallback**: gemini-pro-vision
- **Local Option**: llava-7b
- **Reasoning**: GPT-4o best multimodal, Gemini good alternative

### Fast Simple Tasks
- **Primary**: gpt-3.5-turbo
- **Fallback**: claude-3-haiku-20240307
- **Local Option**: mistral-7b
- **Reasoning**: Speed optimized models for quick responses

## Cost Comparison (per 1M tokens)

| Model | Provider | Type | Input Cost | Output Cost | Context Window |
|-------|----------|------|------------|-------------|----------------|
| codellama-34b | local | local | $0.00 | $0.00 | 32,768 |
| qwen2-5-coder-32b | local | local | $0.00 | $0.00 | 32,768 |
| mixtral-8x7b | local | local | $0.00 | $0.00 | 32,768 |
| deepseek-r1-32b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2-5-32b | local | local | $0.00 | $0.00 | 32,768 |
| llama3-3-70b | local | local | $0.00 | $0.00 | 32,768 |
| qwen2-5-coder-1-5b | local | local | $0.00 | $0.00 | 32,768 |
| gemma2-9b | local | local | $0.00 | $0.00 | 32,768 |
| qwen2-5-7b | local | local | $0.00 | $0.00 | 32,768 |
| qwen2-5-coder-7b | local | local | $0.00 | $0.00 | 32,768 |
| deepseek-r1-8b | local | local | $0.00 | $0.00 | 131,072 |
| phi3-mini | local | local | $0.00 | $0.00 | 32,768 |
| codellama-7b | local | local | $0.00 | $0.00 | 32,768 |
| mistral-7b | local | local | $0.00 | $0.00 | 32,768 |
| llama3-1-8b | local | local | $0.00 | $0.00 | 32,768 |
| qwen3-8b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2-5vl-7b | local | local | $0.00 | $0.00 | 65,536 |
| llama-3.3-70b | local | local | $0.00 | $0.00 | 131,072 |
| deepseek-r1-7b | local | local | $0.00 | $0.00 | 65,536 |
| qwen3-14b | local | local | $0.00 | $0.00 | 131,072 |
| qwen3-32b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2.5-coder-7b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2.5-coder-14b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2.5-coder-32b | local | local | $0.00 | $0.00 | 131,072 |
| qwen2.5-vl-7b | local | local | $0.00 | $0.00 | 65,536 |
| qwen2.5-vl-32b | local | local | $0.00 | $0.00 | 65,536 |
| llava-13b | local | local | $0.00 | $0.00 | 32,768 |
| qwq-32b | local | local | $0.00 | $0.00 | 131,072 |
| llama-3.1-8b | local | local | $0.00 | $0.00 | 131,072 |
| llama-3.1-70b | local | local | $0.00 | $0.00 | 131,072 |
| gemma3-9b | local | local | $0.00 | $0.00 | 131,072 |
| phi4-14b | local | local | $0.00 | $0.00 | 131,072 |
| qwen3-1.7b | local | local | $0.00 | $0.00 | 131,072 |
| gemma3-4b | local | local | $0.00 | $0.00 | 131,072 |
| mistral-nemo-12b | local | local | $0.00 | $0.00 | 131,072 |
| o1-2024-12-17 | openai | hosted | $0.00 | $0.00 | 200,000 |
| gpt-4.1-2025-04-14 | openai | hosted | $0.00 | $0.00 | 8,192 |
| gpt-4.1-mini-2025-04-14 | openai | hosted | $0.00 | $0.00 | 8,192 |
| gpt-4.1-nano-2025-04-14 | openai | hosted | $0.00 | $0.00 | 8,192 |
| gpt-4.1-nano | openai | hosted | $0.00 | $0.00 | 8,192 |
| gemini-pro-vision | google | hosted | $0.00 | $0.00 | 128,000 |
| gpt-4o-mini-2024-07-18 | openai | hosted | $0.00 | $0.00 | 128,000 |
| gpt-4o-mini | openai | hosted | $0.00 | $0.00 | 128,000 |
| gpt-4o-mini-search-preview | openai | hosted | $0.00 | $0.00 | 128,000 |
| grok-3-mini | xai | hosted | $0.00 | $0.00 | 128,000 |
| gemini-2.5-flash | google | hosted | $0.00 | $0.00 | 1,000,000 |
| gpt-4.1-mini | openai | hosted | $0.00 | $0.00 | 8,192 |
| gpt-3.5-turbo | openai | hosted | $0.00 | $0.00 | 16,385 |
| o1-mini-2024-09-12 | openai | hosted | $0.00 | $0.00 | 200,000 |
| o1-mini | openai | hosted | $0.00 | $0.00 | 200,000 |
| o1-pro-2025-03-19 | openai | hosted | $0.00 | $0.01 | 200,000 |
| gemini-2.5-pro | google | hosted | $0.00 | $0.01 | 1,000,000 |
| gemini-pro | google | hosted | $0.00 | $0.01 | 128,000 |
| gpt-3.5-turbo-instruct | openai | hosted | $0.00 | $0.00 | 16,385 |
| gpt-4-0613 | openai | hosted | $0.00 | $0.01 | 8,192 |
| gpt-4o-realtime-preview-2025-06-03 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-audio-preview-2025-06-03 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-3.5-turbo-instruct-0914 | openai | hosted | $0.00 | $0.01 | 16,385 |
| gpt-3.5-turbo-1106 | openai | hosted | $0.00 | $0.01 | 16,385 |
| gpt-4-0125-preview | openai | hosted | $0.00 | $0.01 | 8,192 |
| gpt-3.5-turbo-0125 | openai | hosted | $0.00 | $0.01 | 16,385 |
| gpt-4-turbo-2024-04-09 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-realtime-preview-2024-10-01 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-audio-preview-2024-10-01 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-audio-preview | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-realtime-preview | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-realtime-preview-2024-12-17 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-audio-preview-2024-12-17 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-realtime-preview-2024-12-17 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-audio-preview-2024-12-17 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-realtime-preview | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-audio-preview | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-search-preview-2025-03-11 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-search-preview-2025-03-11 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-transcribe | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-transcribe | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-mini-tts | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4.1 | openai | hosted | $0.00 | $0.01 | 8,192 |
| grok-2-1212 | xai | hosted | $0.00 | $0.01 | 128,000 |
| grok-2-vision-1212 | xai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-2024-08-06 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-2024-11-20 | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-4o-search-preview | openai | hosted | $0.00 | $0.01 | 128,000 |
| gpt-3.5-turbo-16k | openai | hosted | $0.00 | $0.00 | 16,384 |
| grok-3 | xai | hosted | $0.00 | $0.02 | 128,000 |
| grok-3-fast | xai | hosted | $0.00 | $0.02 | 128,000 |
| grok-3-mini-fast | xai | hosted | $0.00 | $0.02 | 128,000 |
| grok-4-0709 | xai | hosted | $0.00 | $0.02 | 128,000 |
| grok-2-image-1212 | xai | hosted | $0.00 | $0.02 | 128,000 |
| gpt-4o-2024-05-13 | openai | hosted | $0.01 | $0.02 | 128,000 |
| chatgpt-4o-latest | openai | hosted | $0.01 | $0.02 | 128,000 |
| gpt-4-1106-preview | openai | hosted | $0.01 | $0.03 | 8,192 |
| gpt-4-turbo-preview | openai | hosted | $0.01 | $0.03 | 128,000 |
| gpt-4-turbo | openai | hosted | $0.01 | $0.03 | 128,000 |
| o1 | openai | hosted | $0.02 | $0.06 | 200,000 |
| claude-opus-4-20250514 | anthropic | hosted | $0.02 | $0.07 | 128,000 |
| claude-sonnet-4-20250514 | anthropic | hosted | $0.02 | $0.07 | 128,000 |
| claude-3-7-sonnet-20250219 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| claude-3-5-sonnet-20241022 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| claude-3-5-haiku-20241022 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| claude-3-5-sonnet-20240620 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| claude-3-haiku-20240307 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| claude-3-opus-20240229 | anthropic | hosted | $0.02 | $0.07 | 200,000 |
| gpt-4 | openai | hosted | $0.03 | $0.06 | 8,192 |
| o1-pro | openai | hosted | $0.15 | $0.60 | 200,000 |

---
*Generated by Enhanced GetAvailableModels.py - Including Grok-4 and Local LLMs*
