---
skill_name: multi-modal
version: "1.0.0"
category: multimodal
trigger: manual
execution_mode: sync
---

# Multi-Modal

## Intent
Process and understand images, audio, and text in unified workflows.

## Supported Modalities

### Images
- Description and analysis
- OCR (text extraction)
- Object detection
- Visual QA
- Chart/graph interpretation

### Audio
- Transcription (speech-to-text)
- Speaker identification
- Sentiment analysis
- Summarization

### Text
- All standard NLP tasks
- Document processing
- Code analysis
- Structured data extraction

## Integration Patterns

### Image + Text
- Analyze image, generate text description
- Extract text from image, process with NLP
- Compare image against text description

### Audio + Text
- Transcribe audio, analyze text
- Generate audio from text (TTS)
- Align audio with text timestamps

### All Modalities
- Video analysis (frames + audio + transcript)
- Multi-modal RAG
- Cross-modal search

## Rules
1. Detect modality automatically when possible
2. Convert to text for reasoning when needed
3. Preserve original data for verification
4. Handle modality-specific errors
5. Optimize for each modality's constraints

## Example
```python
# Process image and generate description
result = await multi_modal.process_image(
    image_data=image_bytes,
    prompt="Describe the chart and extract key data points"
)
# Returns: {"description": "...", "extracted_data": {...}}
```
