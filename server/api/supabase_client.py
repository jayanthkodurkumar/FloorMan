import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase() -> Client:
    return client


def get_authed_supabase(token: str) -> Client:
    """Return a Supabase client authenticated with the user's JWT so RLS policies work."""
    authed = create_client(SUPABASE_URL, SUPABASE_KEY)
    authed.auth.set_session(token, "")
    return authed

