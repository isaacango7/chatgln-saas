from database.supabase import supabase

def get_memory(

    assistant_id,
    phone

):

    response = supabase.table(
        "memory"
    ).select("*").eq(
        "assistant_id",
        assistant_id
    ).eq(
        "phone",
        phone
    ).execute()

    memory = {}

    for item in response.data:

        memory[
            item["memory_key"]
        ] = item["memory_value"]

    return memory


def save_memory(

    assistant_id,
    phone,
    key,
    value

):

    existing = supabase.table(
        "memory"
    ).select("*").eq(
        "assistant_id",
        assistant_id
    ).eq(
        "phone",
        phone
    ).eq(
        "memory_key",
        key
    ).execute()

    if existing.data:

        supabase.table(
            "memory"
        ).update({

            "memory_value":
                value

        }).eq(
            "id",
            existing.data[0]["id"]
        ).execute()

    else:

        supabase.table(
            "memory"
        ).insert({

            "assistant_id":
                assistant_id,

            "phone":
                phone,

            "memory_key":
                key,

            "memory_value":
                value

        }).execute()
