import torch
import torchaudio
from transformers import SeamlessM4Tv2Model, AutoProcessor

def speech_to_text(audio_path: str, model_path: str = "./AI Models/Speech2Text/seamless-m4t-v2-large") -> str:
    """
    Converts speech to text using the SeamlessM4Tv2Model.

    :param audio_path: Path to the input audio file.
    :param model_path: Path or name of the pre-trained model (default: "./AI Models/Speech2Text/seamless-m4t-v2-large").
    :return: Transcribed text from the audio.
    """
    # Load model and processor
    processor = AutoProcessor.from_pretrained(model_path)
    model = SeamlessM4Tv2Model.from_pretrained(model_path)

    # Load and preprocess audio
    waveform, sample_rate = torchaudio.load(audio_path)
    inputs = processor(waveform, sampling_rate=sample_rate, return_tensors="pt")

    # Perform speech-to-text
    with torch.no_grad():
        outputs = model.generate(**inputs)
    
    # Decode and return text
    transcription = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    return transcription

# Example usage
# text = speech_to_text("path/to/audio.wav")
# print(text)