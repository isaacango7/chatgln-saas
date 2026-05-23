from fastapi import APIRouter

from pydantic import BaseModel

from services.assistant_service import (
    get_assistant
)

from services.openai_service import (
    generate_ai_response
)

router = APIRouter()

class AIRequest(BaseModel):

    assistant_id: str

    phone: str

    message: str

@router.post("/ai-response")

def ai_response(data: AIRequest):

    assistant = get_assistant(
        data.assistant_id
    )

    # =========================
    # ASSISTANT NOT FOUND
    # =========================

    if not assistant:

        return {

            "assistant_status":
                False,

            "reply":
                "Assistant introuvable"

        }

    # =========================
    # ASSISTANT DISABLED
    # =========================

    if not assistant[
        "assistant_status"
    ]:

        return {

            "assistant_status":
                False,

            "reply":
                "Assistant désactivé"

        }

    reply = generate_ai_response(

        assistant,

        data.phone,

        data.message

    )

    return {

        "assistant_status":
            True,

        "reply":
            reply

    }
