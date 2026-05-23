from database.supabase import supabase

def get_assistant(
    assistant_id
):

    response = supabase.table(
        "assistants"
    ).select("*").eq(
        "id",
        assistant_id
    ).execute()

    if not response.data:

        return None

    return response.data[0]
