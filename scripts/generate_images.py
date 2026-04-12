"""
Generate module section images for slides using Gemini Imagen 3.
Run from project root:
    .venv/bin/python scripts/generate_images.py
"""

import os
from pathlib import Path
from google import genai
from google.genai import types

API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBFaUGBFBiu6ct2te2R3a2MrPiz4UbvhAo')
OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'slides' / 'public' / 'images'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

PROMPTS = {
    'm1_welcome': (
        "A glowing orange 3D cube floating in a dark space with Python code snippets "
        "faintly visible in the background. Clean, modern, minimalist style. "
        "No text. Wide aspect ratio."
    ),
    'm2_fundamentals': (
        "A clean 3D architectural wireframe of a simple room interior — floor, four walls, "
        "a table and a sphere lamp — rendered in soft blue and white tones on a dark background. "
        "Technical, geometric, minimalist. No text."
    ),
    'm3_interaction': (
        "A modern game controller held in hands, with a glowing 3D virtual environment "
        "reflected on the controller surface. Dark background, vibrant colors. No text."
    ),
    'm4_experiment': (
        "An abstract visualization of a psychology experiment timeline — colored state blocks "
        "(blue, yellow, green, purple) connected by arrows on a dark background, "
        "with subtle EEG waveforms in the background. Scientific, clean. No text."
    ),
    'm5_mazewalker': (
        "A top-down view of a 3D maze with brick walls, soft lighting, "
        "and a small glowing marker showing a navigation path. "
        "Dark background, cinematic style. No text."
    ),
    'm6_vr': (
        "A close-up of a high-end VR headset (futuristic, sleek design) "
        "with a virtual 3D room visible through the lenses. "
        "Dark background, dramatic lighting. No text."
    ),
    'm7_models': (
        "Two elegant 3D models — an angel statue and a playground swing — "
        "placed inside a softly lit room with grass floor and brick walls. "
        "Cinematic lighting, photorealistic style. No text."
    ),
}


def generate(name, prompt):
    print(f'Generating: {name}...', end=' ', flush=True)
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE', 'TEXT'],
        ),
    )
    out_path = OUTPUT_DIR / f'{name}.png'
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            with open(str(out_path), 'wb') as f:
                f.write(image_data)
            print(f'saved → {out_path.name}')
            return
    print('no image in response')


if __name__ == '__main__':
    import sys
    targets = sys.argv[1:] or list(PROMPTS.keys())
    for name in targets:
        if name in PROMPTS:
            generate(name, PROMPTS[name])
        else:
            print(f'Unknown target: {name}')
    print('Done.')
