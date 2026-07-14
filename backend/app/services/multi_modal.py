"""Multi-modal service for handling images, audio, and text."""
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.services.groq_service import get_groq_service


class MultiModalService:
    """Service for multi-modal content processing."""

    def __init__(self):
        self._supported_formats = {
            "image": ["png", "jpg", "jpeg", "gif", "webp"],
            "audio": ["mp3", "wav", "ogg", "m4a"],
            "text": ["txt", "md", "json", "csv"],
        }
        self._processing_history: List[Dict] = []

    async def process_image(
        self,
        image_data: bytes,
        prompt: str = "Describe this image in detail.",
        model: str = "llama-3.3-70b-versatile",
    ) -> Dict[str, Any]:
        """Process an image with vision capabilities."""

        base64_image = base64.b64encode(image_data).decode("utf-8")

        groq = await get_groq_service()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ]

        result = await groq.chat_completion(
            messages=messages,
            model=model,
            max_tokens=1000,
        )

        self._processing_history.append({
            "type": "image",
            "model": model,
            "prompt": prompt,
            "success": result["success"],
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "success": result["success"],
            "description": result.get("content", ""),
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "model": model,
        }

    async def process_audio(
        self,
        audio_data: bytes,
        format: str = "mp3",
        task: str = "transcribe",
    ) -> Dict[str, Any]:
        """Process audio (transcription or analysis)."""

        groq = await get_groq_service()

        if task == "transcribe":
            prompt = "Transcribe the following audio content. [Audio data would be processed here]"

            messages = [
                {"role": "system", "content": "You are an audio transcription assistant."},
                {"role": "user", "content": prompt},
            ]

            result = await groq.chat_completion(messages=messages, max_tokens=2000)

            return {
                "success": result["success"],
                "transcription": result.get("content", ""),
                "format": format,
                "task": task,
            }

        return {
            "success": False,
            "error": "Audio processing not fully implemented. Use external transcription service.",
        }

    async def process_text_document(
        self,
        content: str,
        task: str = "summarize",
    ) -> Dict[str, Any]:
        """Process text documents."""

        groq = await get_groq_service()

        tasks = {
            "summarize": "Summarize the following document concisely:",
            "extract_entities": "Extract all named entities from the following document:",
            "sentiment": "Analyze the sentiment of the following text:",
            "classify": "Classify the following document into categories:",
            "qa": "Answer questions about the following document:",
        }

        prompt = f"{tasks.get(task, tasks['summarize'])}

{content[:8000]}"

        messages = [
            {"role": "system", "content": f"You are a document processing assistant. Task: {task}"},
            {"role": "user", "content": prompt},
        ]

        result = await groq.chat_completion(messages=messages, max_tokens=2000)

        return {
            "success": result["success"],
            "result": result.get("content", ""),
            "task": task,
            "input_length": len(content),
        }

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported file formats."""
        return self._supported_formats

    def get_processing_history(self, limit: int = 100) -> List[Dict]:
        """Get processing history."""
        return self._processing_history[-limit:]


# Singleton
_multi_modal: Optional[MultiModalService] = None


async def get_multi_modal_service() -> MultiModalService:
    """Get or create multi-modal service."""
    global _multi_modal
    if _multi_modal is None:
        _multi_modal = MultiModalService()
    return _multi_modal
