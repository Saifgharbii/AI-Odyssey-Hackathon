from huggingface_hub import snapshot_download
snapshot_download(repo_id="parler-tts/parler-tts-mini-v1.1", local_dir="../../AI Models/Text2Speech/parler-tts-mini-v1.1")

import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import io


def generate_speech(prompt: str, description: str, model_path: str = "../../AI Models/Text2Speech/parler-tts-mini-v1.1") -> bytes:
    """
    Generates speech from text using ParlerTTS and returns the audio as bytes.

    Args:
        prompt (str): The text to be converted into speech.
        description (str): The description of the speaker's style and tone.
        model_path (str): Path to the locally stored ParlerTTS model.

    Returns:
        bytes: The generated audio in WAV format as bytes.
    """
    try:
        # Set device (GPU if available, otherwise CPU)
        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        # Load model and tokenizers
        model = ParlerTTSForConditionalGeneration.from_pretrained(model_path).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

        # Tokenize inputs
        input_ids = description_tokenizer(description, return_tensors="pt").input_ids.to(device)
        prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

        # Generate speech
        generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
        audio_arr = generation.cpu().numpy().squeeze()

        # Save audio to a bytes buffer instead of a file
        buffer = io.BytesIO()
        sf.write(buffer, audio_arr, model.config.sampling_rate, format="WAV")
        buffer.seek(0)  # Reset buffer position to the beginning

        return buffer.read()  # Return audio as bytes

    except Exception as e:
        raise RuntimeError(f"Failed to generate speech: {str(e)}")
