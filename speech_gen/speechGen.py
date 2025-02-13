from huggingface_hub import snapshot_download
snapshot_download(repo_id="parler-tts/parler-tts-mini-v1.1", local_dir="AI Models/Text2Speech/parler-tts-mini-v1.1")

import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

def generate_speech(prompt, description, model_path="./AI Models/Text2Speech/parler-tts-mini-v1.1", output_file="parler_tts_out.wav"):
    """
    Generates speech from text using ParlerTTS and saves the output as a WAV file.

    :param prompt: The text to be converted into speech.
    :param description: The description of the speaker's style and tone.
    :param model_path: Path to the locally stored ParlerTTS model.
    :param output_file: Name of the output audio file.
    """
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

    # Save to file
    sf.write(output_file, audio_arr, model.config.sampling_rate)

    return output_file  # Return the output file path for reference



