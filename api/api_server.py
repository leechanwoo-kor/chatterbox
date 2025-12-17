"""
Chatterbox TTS API Server
FastAPI-based REST API for Chatterbox TTS models
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
import torch
import torchaudio as ta
import io
import tempfile
import os
from pathlib import Path
import logging
import sys

# Add parent directory to path to import chatterbox
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chatterbox.tts_turbo import ChatterboxTurboTTS
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

try:
    from config import settings
except ImportError:
    # Fallback if config is not available
    class Settings:
        api_title = "Chatterbox TTS API"
        api_version = "1.0.0"
        api_description = "REST API for Chatterbox Text-to-Speech models by Resemble AI"
        allow_origins = ["*"]
        allow_credentials = True
        allow_methods = ["*"]
        allow_headers = ["*"]
        max_text_length = 5000
        device = None
        hf_token = None
    settings = Settings()

# Set Hugging Face token if available
if settings.hf_token:
    os.environ['HF_TOKEN'] = settings.hf_token
    os.environ['HUGGING_FACE_HUB_TOKEN'] = settings.hf_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)

# Global model storage
class ModelManager:
    def __init__(self):
        self.turbo_model = None
        self.multilingual_model = None
        self.original_model = None
        self.device = self._get_device()

    def _get_device(self):
        """Automatically detect the best available device"""
        if settings.device:
            return settings.device
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def load_turbo(self):
        """Load Turbo model"""
        if self.turbo_model is None:
            logger.info(f"Loading Chatterbox-Turbo model on {self.device}...")
            self.turbo_model = ChatterboxTurboTTS.from_pretrained(device=self.device)
            logger.info("Chatterbox-Turbo model loaded successfully")
        return self.turbo_model

    def load_multilingual(self):
        """Load Multilingual model"""
        if self.multilingual_model is None:
            logger.info(f"Loading Chatterbox-Multilingual model on {self.device}...")
            self.multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
            logger.info("Chatterbox-Multilingual model loaded successfully")
        return self.multilingual_model

    def load_original(self):
        """Load Original model"""
        if self.original_model is None:
            logger.info(f"Loading Chatterbox (Original) model on {self.device}...")
            self.original_model = ChatterboxTTS.from_pretrained(device=self.device)
            logger.info("Chatterbox (Original) model loaded successfully")
        return self.original_model

model_manager = ModelManager()

# Pydantic models for request/response
class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    model_type: Literal["turbo", "multilingual", "original"] = Field(
        default="turbo",
        description="Model type to use"
    )
    language_id: Optional[str] = Field(
        None,
        description="Language ID for multilingual model (e.g., 'ko', 'en', 'ja', 'zh')"
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Hello, this is a test of the Chatterbox TTS system.",
                "model_type": "turbo",
                "language_id": None
            }
        }

class HealthResponse(BaseModel):
    status: str
    device: str
    loaded_models: list[str]

# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Chatterbox TTS API",
        "version": "1.0.0",
        "description": "REST API for Chatterbox Text-to-Speech models",
        "endpoints": {
            "POST /tts": "Generate speech from text",
            "POST /tts/turbo": "Generate speech using Turbo model",
            "POST /tts/multilingual": "Generate speech using Multilingual model",
            "POST /tts/original": "Generate speech using Original model",
            "POST /tts/with-voice": "Generate speech with custom voice reference",
            "GET /health": "Health check",
            "GET /models": "List available models"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    loaded = []
    if model_manager.turbo_model is not None:
        loaded.append("turbo")
    if model_manager.multilingual_model is not None:
        loaded.append("multilingual")
    if model_manager.original_model is not None:
        loaded.append("original")

    return {
        "status": "healthy",
        "device": model_manager.device,
        "loaded_models": loaded
    }

@app.get("/models")
async def list_models():
    """List available models and their capabilities"""
    return {
        "models": {
            "turbo": {
                "size": "350M",
                "languages": ["en"],
                "features": ["Paralinguistic tags ([laugh], [cough], [chuckle])", "Low compute", "Fast generation"],
                "best_for": "Zero-shot voice agents, Production"
            },
            "multilingual": {
                "size": "500M",
                "languages": ["ar", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "it", "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sv", "sw", "tr", "zh"],
                "features": ["Zero-shot cloning", "Multiple languages"],
                "best_for": "Global applications, Localization"
            },
            "original": {
                "size": "500M",
                "languages": ["en"],
                "features": ["CFG tuning", "Exaggeration tuning"],
                "best_for": "General zero-shot TTS with creative controls"
            }
        }
    }

@app.post("/tts")
async def generate_tts(request: TTSRequest):
    """
    Generate speech from text using specified model

    - **text**: Text to convert to speech
    - **model_type**: Model to use (turbo, multilingual, original)
    - **language_id**: Language ID for multilingual model (optional)
    """
    try:
        # Validate text length
        if len(request.text) > settings.max_text_length:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long. Maximum length is {settings.max_text_length} characters."
            )
        # Load appropriate model
        if request.model_type == "turbo":
            model = model_manager.load_turbo()
        elif request.model_type == "multilingual":
            model = model_manager.load_multilingual()
        elif request.model_type == "original":
            model = model_manager.load_original()
        else:
            raise HTTPException(status_code=400, detail="Invalid model_type")

        # Generate audio
        logger.info(f"Generating audio with {request.model_type} model: {request.text[:50]}...")

        if request.model_type == "multilingual" and request.language_id:
            wav = model.generate(request.text, language_id=request.language_id)
        else:
            wav = model.generate(request.text)

        # Save to memory buffer
        buffer = io.BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)

        logger.info("Audio generation completed successfully")

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            }
        )

    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/turbo")
async def generate_tts_turbo(
    text: str = Form(..., description="Text to convert to speech"),
):
    """
    Generate speech using Chatterbox-Turbo model
    Supports paralinguistic tags: [laugh], [cough], [chuckle]
    """
    try:
        model = model_manager.load_turbo()

        logger.info(f"Generating audio with Turbo model: {text[:50]}...")
        wav = model.generate(text)

        buffer = io.BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)

        logger.info("Audio generation completed successfully")

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=turbo_output.wav"
            }
        )

    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/multilingual")
async def generate_tts_multilingual(
    text: str = Form(..., description="Text to convert to speech"),
    language_id: str = Form("en", description="Language ID (e.g., 'ko', 'en', 'ja', 'zh')"),
):
    """
    Generate speech using Chatterbox-Multilingual model
    Supports 23+ languages
    """
    try:
        model = model_manager.load_multilingual()

        logger.info(f"Generating audio with Multilingual model ({language_id}): {text[:50]}...")
        wav = model.generate(text, language_id=language_id)

        buffer = io.BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)

        logger.info("Audio generation completed successfully")

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=multilingual_{language_id}_output.wav"
            }
        )

    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/original")
async def generate_tts_original(
    text: str = Form(..., description="Text to convert to speech"),
):
    """
    Generate speech using Chatterbox (Original) model
    """
    try:
        model = model_manager.load_original()

        logger.info(f"Generating audio with Original model: {text[:50]}...")
        wav = model.generate(text)

        buffer = io.BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)

        logger.info("Audio generation completed successfully")

        return StreamingResponse(
            buffer,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=original_output.wav"
            }
        )

    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/with-voice")
async def generate_tts_with_voice(
    text: str = Form(..., description="Text to convert to speech"),
    model_type: str = Form("turbo", description="Model type (turbo, multilingual, original)"),
    language_id: Optional[str] = Form(None, description="Language ID for multilingual model"),
    voice_file: UploadFile = File(..., description="Reference voice audio file (WAV format recommended)"),
):
    """
    Generate speech with custom voice reference
    Upload a reference audio file to clone the voice
    """
    try:
        # Load appropriate model
        if model_type == "turbo":
            model = model_manager.load_turbo()
        elif model_type == "multilingual":
            model = model_manager.load_multilingual()
        elif model_type == "original":
            model = model_manager.load_original()
        else:
            raise HTTPException(status_code=400, detail="Invalid model_type")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await voice_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            logger.info(f"Generating audio with {model_type} model and custom voice: {text[:50]}...")

            # Generate with voice reference
            if model_type == "multilingual" and language_id:
                wav = model.generate(text, audio_prompt_path=tmp_path, language_id=language_id)
            else:
                wav = model.generate(text, audio_prompt_path=tmp_path)

            # Save to memory buffer
            buffer = io.BytesIO()
            ta.save(buffer, wav, model.sr, format="wav")
            buffer.seek(0)

            logger.info("Audio generation with custom voice completed successfully")

            return StreamingResponse(
                buffer,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": f"attachment; filename={model_type}_custom_voice_output.wav"
                }
            )

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Error generating TTS with custom voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
