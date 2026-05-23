import os
import json
import time

from openai import OpenAI

from database.supabase import supabase

from services.memory_service import (

    get_memory,
    save_memory

)

client = OpenAI(

    api_key=os.getenv(
        "OPENAI_API_KEY"
    )

)

def generate_ai_response(

    assistant,
    phone,
    user_message

):

    assistant_id = assistant["id"]

    # =========================
    # MEMORY
    # =========================

    memory = get_memory(

        assistant_id,
        phone

    )

    # =========================
    # HISTORY
    # =========================

    history_response = supabase.table(
        "conversations"
    ).select("*").eq(
        "assistant_id",
        assistant_id
    ).eq(
        "phone",
        phone
    ).order(
        "created_at",
        desc=True
    ).limit(30).execute()

    history = history_response.data[::-1]

    # =========================
    # GREETING DETECTION
    # =========================

    first_message = (
        len(history) == 0
    )

    # =========================
    # SYSTEM PROMPT
    # =========================

    system_prompt = f"""

Vous êtes l'assistant officiel de :

{assistant['business_name']}

RÈGLES ABSOLUES :

- Ne jamais inventer
- Ne jamais créer faux prix
- Ne jamais créer faux produits
- Ne jamais créer fausse disponibilité

- Si information absente :

dire simplement :

"Je ne dispose pas encore
de cette information."

- Toujours vouvoyer
- Être naturel
- Être humain
- Être professionnel
- Être commercial
- Réponses courtes

DESCRIPTION ENTREPRISE :

{assistant['business_description']}

INSTRUCTIONS :

{assistant['instructions']}

PRODUITS :

{assistant['products']}

MÉMOIRE CLIENT :

{memory}

"""

    if first_message:

        system_prompt += """

La première réponse doit :

- saluer le client
- présenter brièvement l'entreprise
- être chaleureuse
- professionnelle
"""

    # =========================
    # BUILD MESSAGES
    # =========================

    messages = [

        {

            "role":
                "system",

            "content":
                system_prompt

        }

    ]

    for item in history:

        messages.append({

            "role":
                item["role"],

            "content":
                item["message"]

        })

    messages.append({

        "role":
            "user",

        "content":
            user_message

    })

    # =========================
    # OPENAI RESPONSE
    # =========================

    completion = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=messages,

        temperature=0.4

    )

    reply = completion.choices[
        0
    ].message.content

    tokens = completion.usage.total_tokens

    # =========================
    # SAVE TOKENS
    # =========================

    current_tokens = assistant[
        "total_tokens"
    ] or 0

    supabase.table(
        "assistants"
    ).update({

        "total_tokens":

            current_tokens + tokens

    }).eq(

        "id",
        assistant_id

    ).execute()

    # =========================
    # SAVE CONVERSATION
    # =========================

    supabase.table(
        "conversations"
    ).insert([

        {

            "assistant_id":
                assistant_id,

            "phone":
                phone,

            "role":
                "user",

            "message":
                user_message

        },

        {

            "assistant_id":
                assistant_id,

            "phone":
                phone,

            "role":
                "assistant",

            "message":
                reply

        }

    ]).execute()

    # =========================
    # MEMORY EXTRACTION
    # =========================

    extraction = client.chat.completions.create(

        model="gpt-4.1-mini",

        temperature=0,

        messages=[

            {

                "role":
                    "system",

                "content":
"""
Extrait uniquement
les informations utiles
sur le client.

Retourne uniquement JSON.

Exemple :

{
  "city":"Kinshasa",
  "favorite_brand":"Nike"
}

Sinon :
{}
"""
            },

            {

                "role":
                    "user",

                "content":
                    user_message

            }

        ]

    )

    try:

        extracted = json.loads(

            extraction.choices[
                0
            ].message.content

        )

        for key, value in extracted.items():

            save_memory(

                assistant_id,
                phone,
                key,
                str(value)

            )

    except:

        pass

    # =========================
    # HUMAN DELAY
    # =========================

    time.sleep(30)

    return reply
