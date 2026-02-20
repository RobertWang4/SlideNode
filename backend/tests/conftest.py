import os

# Set default env vars for tests before any app imports
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("AUTH0_SKIP_VERIFY", "true")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("POSTGRES_DSN", "sqlite:///./test_slidenode.db")
