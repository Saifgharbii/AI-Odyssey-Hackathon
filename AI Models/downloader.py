from huggingface_hub import snapshot_download

snapshot_download(repo_id="facebook/seamless-m4t-v2-large", local_dir="AI Models/Speech2Text/seamless-m4t-v2-large")
snapshot_download(repo_id="stable-diffusion-v1-5/stable-diffusion-v1-5", local_dir="AI Models/Text2Image/stable-diffusion-v1-5")
snapshot_download(repo_id="NimVideo/cogvideox-2b-img2vid", local_dir="AI Models/Video-Image2Video/cogvideox-2b-img2vid")
snapshot_download(repo_id="parler-tts/parler-tts-mini-v1.1", local_dir="AI Models/Text2Speech/parler-tts-mini-v1.1")

