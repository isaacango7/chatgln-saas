from fastapi import FastAPI

from pydantic import BaseModel

from supabase import create_client

from dotenv import load_dotenv

from openai import OpenAI

import os


# =========================
# LOAD ENV
# =========================

load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY"
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)


# =========================
# CLIENTS
# =========================

supabase = create_client(

    SUPABASE_URL,

    SUPABASE_KEY

)

openai = OpenAI(

    api_key=OPENAI_API_KEY

)


# =========================
# FASTAPI
# =========================

app = FastAPI()


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {

        "message":
        "ChatGLN Backend Online 🚀"

    }


# =========================
# REQUEST MODEL
# =========================

class AIRequest(BaseModel):

    assistant_id: str

    phone: str

    message: str


# =========================
# GET ASSISTANT
# =========================

def get_assistant(

    assistant_id

):

    response = (

        supabase

        .table("assistants")

        .select("*")

        .eq(
            "id",
            assistant_id
        )

        .limit(1)

        .execute()

    )

    data = response.data

    if not data:

        return None

    return data[0]


# =========================
# SAVE MESSAGE
# =========================

def save_message(

    phone,

    role,

    message

):

    supabase.table(
        "conversations"
    ).insert({

        "phone":
            phone,

        "role":
            role,

        "message":
            message

    }).execute()


# =========================
# GET HISTORY
# =========================

def get_history(phone):

    response = (

        supabase

        .table("conversations")

        .select("*")

        .eq(
            "phone",
            phone
        )

        .order(
            "created_at",
            desc=False
        )

        .limit(20)

        .execute()

    )

    history = []

    for item in response.data:

        history.append({

            "role":
                item["role"],

            "content":
                item["message"]

        })

    return history


# =========================
# GENERATE REPLY
# =========================

def generate_reply(

    assistant,

    history,

    user_message

):

    prompt = f"""

You are the official WhatsApp assistant
of this business.

BUSINESS NAME:
{assistant["boutique_name"]}

BUSINESS DESCRIPTION:
{assistant["description"]}

BUSINESS INSTRUCTIONS:
{assistant["instructions"]}

BUSINESS SALES STRATEGY:
{assistant["sales_strategy"]}

CONVERSATION HISTORY:
{history}

CUSTOMER MESSAGE:
{user_message}

STRICT RULES:

- NEVER invent products
- NEVER invent services
- ONLY use provided business information
- If information is unavailable,
say politely that the business
did not provide it

- Human WhatsApp tone
- Short messages
- Natural seller tone
- No repeated greetings
- No robotic style
- Focus on helping customer
- Focus on conversion

"""

    response = (

        openai.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[

                {

                    "role":
                    "system",

                    "content":
                    "You are a professional business WhatsApp seller."

                },

                {

                    "role":
                    "user",

                    "content":
                    prompt

                }

            ],

            temperature=0.5

        )

    )

    return (

        response

        .choices[0]

        .message

        .content

    )


# =========================
# MAIN API
# =========================

@app.post("/ai-response")
def ai_response(data: AIRequest):

    assistant = get_assistant(

        data.assistant_id

    )

    if not assistant:

        return {

            "assistant_status":
                False
        }

    if (

        assistant[
            "assistant_status"
        ] is False

    ):

        return {

            "assistant_status":
                False
        }

    phone = data.phone

    user_message = data.message

    save_message(

        phone,

        "user",

        user_message

    )

    history = get_history(
        phone
    )

    reply = generate_reply(

        assistant,

        history,

        user_message

    )

    save_message(

        phone,

        "assistant",

        reply

    )

    return {

        "assistant_status":
            True,

        "reply":
            reply

    }
