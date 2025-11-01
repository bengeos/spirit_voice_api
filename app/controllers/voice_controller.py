from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/voice")
async def voice_controller(voice: UploadFile = File(...)):
    """
    Accepts user voice and returns AI voice.
    """
    # TODO: Replace with voice processing pipeline
    contents = await voice.read()
    return {"filename": "voice", "length": len(contents)}
