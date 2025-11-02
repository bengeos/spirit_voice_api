from fastapi import APIRouter, File, UploadFile
from app.services.audio_service import AudioService
from app.services.advice_service import BiblicalAdvisor
from app.config.settings import get_settings

router = APIRouter()


@router.post("/voice")
async def voice_controller(voice: UploadFile = File(...)):
    """
    Accepts user voice and returns AI voice.
    """
    file = await voice.read()
    audio_service = AudioService(get_settings().EDEN_API_TOKEN, file)
    biblical_adviser = BiblicalAdvisor()
    try:
        text_request = audio_service.speech_to_text()
        english_request = audio_service.translate_text(text_request)
        answer = biblical_adviser.generate_advice(english_request)
        native_answer = biblical_adviser.translate(answer, "am")
        audio_url = audio_service.text_to_speech(native_answer)
    except Exception as e:
        return {"error": f"an error occured {e}"}
    return {
        "answer_url": audio_url,
        "text": native_answer
    }
