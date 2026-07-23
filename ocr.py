import torch
from transformers import AutoModelForImageTextToText, AutoProcessor
from transformers.image_utils import load_image

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    DTYPE = torch.float16
    ATTENTION_IMPLEMENTATION = "flash_attention_2"
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
    DTYPE = torch.float16
    ATTENTION_IMPLEMENTATION = "eager"
else:
    DEVICE = torch.device("cpu")
    DTYPE = torch.float32
    ATTENTION_IMPLEMENTATION = "eager"

PROMPT = "Describe this image in at most eight words. Output only the description."


class OCR:
    def __init__(self, image_path):
        self.image = load_image(image_path)
        print(f"Loading SmolVLM on {DEVICE}...", flush=True)
        self.processor = AutoProcessor.from_pretrained(
            "HuggingFaceTB/SmolVLM-256M-Instruct",
            local_files_only=True,
        )
        self.model = AutoModelForImageTextToText.from_pretrained(
            "HuggingFaceTB/SmolVLM-256M-Instruct",
            local_files_only=True,
            dtype=DTYPE,
            _attn_implementation=ATTENTION_IMPLEMENTATION,
        ).to(DEVICE)
        print("Model loaded.", flush=True)

    def generate(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": PROMPT}
                ]
            },
        ]

        prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=prompt, images=[self.image], return_tensors="pt")
        inputs = inputs.to(DEVICE)

        print("Generating description...", flush=True)
        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=False,
            )

        prompt_length = inputs["input_ids"].shape[1]
        generated_ids = generated_ids[:, prompt_length:]
        generated_texts = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )

        words = generated_texts[0].split()[:8]
        return " ".join(words).rstrip(" ,.;:-")


if __name__ == "__main__":
    image_path = "https://www.braveheartsalliance.org/pictures/home/2.jpg"
    ocr = OCR(image_path=image_path)
    print(ocr.generate())
