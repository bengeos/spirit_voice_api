from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/voice")
def voice_controller(voice: UploadFile = File(...)):
    """
    Accepts user voice and returns AI voice.
    """
    contents = voice.read()
    return {"filename": "voice", "length": len(contents)}
