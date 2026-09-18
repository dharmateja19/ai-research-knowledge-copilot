import hashlib
import json

import redis


REDIS_URL = "redis://localhost:6379/0"

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def set_cache(key: str, value: str, expire: int = 3600):
    redis_client.set(
        key,
        value,
        ex=expire
    )


def get_cache(key: str):
    return redis_client.get(key)


def delete_cache(key: str):
    redis_client.delete(key)


def build_chat_cache_key(
    conversation_id,
    question,
    document_ids,
    route
):
    data = {
        "conversation_id": conversation_id,
        "question": question.strip().lower(),
        "document_ids": sorted(document_ids),
        "route": route
    }

    raw = json.dumps(
        data,
        sort_keys=True
    )

    digest = hashlib.sha256(
        raw.encode()
    ).hexdigest()

    return f"chat:{conversation_id}:{digest}"