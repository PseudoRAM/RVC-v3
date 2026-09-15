import sys
from pathlib import Path

from cog import BasePredictor, Input, Path as CogPath

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from service import VoiceService


class Predictor(BasePredictor):
    def setup(self):
        self.service = VoiceService()

    def predict(
        self,
        input_audio: CogPath = Input(description="Audio to convert."),
        rvc_model: str = Input(default="CUSTOM", description="Provisioned voice directory name, or supply a custom model URL."),
        custom_rvc_model_download_url: str = Input(default=None, description="ZIP URL with one RVC checkpoint and optional index."),
        pitch_change: float = Input(default=0, description="Pitch shift in semitones."),
        index_rate: float = Input(default=0.5, ge=0, le=1),
        filter_radius: int = Input(default=3, ge=0, le=7),
        rms_mix_rate: float = Input(default=0.25, ge=0, le=1),
        f0_method: str = Input(default="rmvpe", choices=["rmvpe", "mangio-crepe"]),
        crepe_hop_length: int = Input(default=160, ge=1, le=1024, description="Pitch analysis hop in samples at 16 kHz."),
        protect: float = Input(default=0.33, ge=0, le=0.5),
        output_format: str = Input(default="wav", choices=["wav", "mp3"]),
        use_index: bool = Input(default=False, description="Enable retrieval; changes audio and adds processing."),
        refresh_custom_model: bool = Input(default=False, description="Redownload a cached custom voice."),
    ) -> CogPath:
        return CogPath(self.service.convert(
            input_audio, rvc_model, custom_rvc_model_download_url, refresh_custom_model,
            pitch_change, index_rate, filter_radius, rms_mix_rate, protect,
            f0_method, crepe_hop_length, output_format, use_index))
