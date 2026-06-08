"""Clean baseline service — only EU endpoints, no secrets, no PII."""
import os

ENDPOINT = "https://eu-central-1.bedrock.example/invoke"
API_KEY = os.environ["PRIMARY_API_KEY"]  # aus Env, kein Klartext


def call_model(prompt: str) -> str:
    # Routing ausschliesslich ueber EU-Endpunkt (Gate E1).
    return f"POST {ENDPOINT} len={len(prompt)}"
