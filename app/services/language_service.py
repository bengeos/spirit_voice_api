import requests
import time


class LanguageDetection:
    def __init__(self, api_key, file_path):
        self.api_key = api_key
        self.file_path = file_path

    def _stt(self):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = "https://api.edenai.run/v2/audio/speech_to_text_async"
        data = {
            "providers": "google",
            "language": "en-US",
        }

        files = {"file": open(self.file_path, "rb")}
        response = requests.post(url, data=data, files=files, headers=headers)
        print(response.json())
        job_id = response.json()["public_id"]
        url = f"https://api.edenai.run/v2/audio/speech_to_text_async/{job_id}/?response_as_dict=true&show_base_64=true&show_original_response=false"
        headers = {"accept": "application/json"}

        timeout = 120
        interval = 2
        start = time.time()

        while True:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers)
            print(response.json())
            try:
                status = response.json().get("status")
            except ValueError:
                status = None

            if status == "finished":
                break
            if status == "failed":
                raise RuntimeError(
                    f"Transcription job failed: {response.text}",
                )
            if time.time() - start > timeout:
                raise TimeoutError(
                    "Timed out waiting for transcription to finish",
                )

            time.sleep(interval)
        text = response.json()["results"]["google"]["text"]
        return text

    def _identify_language(self, text: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = "https://api.edenai.run/v2/translation/language_detection"
        payload = {
            "providers": "google",
            "text": text,
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.json())
        return response.json()["google"]["items"][0]["display_name"]

    def detect_language(self):
        text = self._stt()
        return self._identify_language(text)
