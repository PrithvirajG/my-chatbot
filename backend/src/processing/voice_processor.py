import numpy as np
import torchaudio
from loguru import logger
from ..core.model_router import model_router
from ..core.config_loader import settings

class VoiceProcessor:
    def __init__(self):
        self.voice_model = model_router.get_model("voice")
        self.sample_rate = 16000  # Whisper requires 16kHz

    def _load_audio(self, audio_data: bytes) -> np.ndarray:
        """Convert bytes to audio tensor"""
        try:
            waveform, sample_rate = torchaudio.load(BytesIO(audio_data))
            
            # Resample if needed
            if sample_rate != self.sample_rate:
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sample_rate,
                    new_freq=self.sample_rate
                )
                waveform = resampler(waveform)
                
            return waveform.mean(dim=0).numpy()  # Convert to mono
        except Exception as e:
            logger.error(f"Audio loading failed: {str(e)}")
            raise ValueError("Invalid audio data")

    def transcribe_audio(self, audio_data: bytes) -> dict:
        """Transcribe audio using voice model"""
        try:
            audio_array = self._load_audio(audio_data)
            result = self.voice_model.transcribe(audio_array)
            
            return {
                "text": result["text"],
                "language": result["language"],
                "duration": result["segments"][-1]["end"] if result["segments"] else 0
            }
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise RuntimeError("Audio processing error")

voice_processor = VoiceProcessor()