import io
import requests
import time
from typing import BinaryIO


class AudioService:
    def __init__(self, api_key, file: BinaryIO):
        self.api_key = api_key
        self.file = file

    def speech_to_text(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = "https://api.edenai.run/v2/audio/speech_to_text_async"
        data = {
            "providers": "google",
            "language": "am",
        }

        files = {"file": ("audio.wav", io.BytesIO(self.file), "audio/wav")}
        response = requests.post(url, data=data, files=files, headers=headers)

        try:
            job_id = response.json()["public_id"]
        except Exception:
            raise ValueError()
        url = f"https://api.edenai.run/v2/audio/speech_to_text_async/{job_id}/?response_as_dict=true&show_base_64=true&show_original_response=false"
        headers = {"accept": "application/json"}

        timeout = 120
        interval = 2
        start = time.time()

        while True:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers)

            try:
                status = response.json().get("status")
            except ValueError:
                status = None

            if status == "finished":
                break
            if status == "failed":
                raise RuntimeError(f"Transcription job failed: {response.text}")
            if time.time() - start > timeout:
                raise TimeoutError("Timed out waiting for transcription to finish")

            time.sleep(interval)
        text = response.json()["results"]["google"]["text"]
        return text

    def text_to_speech(self, text: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = "https://api.edenai.run/v2/audio/text_to_speech"
        payload = {
            "providers": "microsoft",
            "language": "am",
            "option": "FEMALE",
            "text": text,
        }

        response = requests.post(url, json=payload, headers=headers)
        result = response.json()["microsoft"]["audio_resource_url"]
        return result

    def translate_text(self, text: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = "https://api.edenai.run/v2/translation/automatic_translation"
        payload = {
            "providers": "google",
            "source_language": "am",
            "target_language": "en",
            "text": text,
        }

        response = requests.post(url, json=payload, headers=headers)

        result = response.json()["google"]["text"]
        return result
