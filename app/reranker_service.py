from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


def rerank_results(query: str, results: list, top_k: int = 5):
    if not results:
        return []

    pairs = [
        (query, result["text"])
        for result in results
    ]

    scores = reranker.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):
        result_copy = result.copy()
        result_copy["rerank_score"] = float(score)
        reranked.append(result_copy)

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]