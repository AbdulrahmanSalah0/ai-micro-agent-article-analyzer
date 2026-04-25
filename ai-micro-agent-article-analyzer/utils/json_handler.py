# utils/json_handler.py

import json


def deduplicate_technologies(technologies: list) -> list:
    """
    Remove duplicate technologies while preserving order.
    Uses normalization for better matching.
    """

    seen = set()
    unique = []

    for tech in technologies:
        normalized = (
            tech.strip()
            .lower()
            .replace("-", " ")
            .replace("_", " ")
        )

        if normalized not in seen:
            seen.add(normalized)
            unique.append(tech.strip())

    return unique


def estimate_confidence(summary: list, technologies: list) -> float:
    """
    Estimate confidence score for extracted AI insights.
    """

    if not summary or not technologies:
        return 0.4

    score = 0.5

    # Validate summary quality
    valid_summary_points = [
        point for point in summary
        if isinstance(point, str) and len(point.split()) >= 5
    ]

    score += min(len(valid_summary_points) * 0.08, 0.24)

    # Evaluate technologies quality
    meaningful_techs = [
        t for t in technologies
        if isinstance(t, str) and len(t.strip()) > 1
    ]

    score += min(len(meaningful_techs) * 0.025, 0.21)

    return round(min(score, 0.95), 2)


def format_output(
    url: str,
    summary: list,
    technologies: list,
    status: str,
    processing_time: float = None,
    chunks_used: int = None
) -> dict:
    """
    Format final output with metadata.
    """

    return {
        "url": url,
        "summary": summary,
        "technologies": technologies,
        "status": status,
        "metadata": {
            "processing_time": processing_time,
            "chunks_used": chunks_used
        },
        "confidence": estimate_confidence(summary, technologies)
    }


def save_to_json(data: dict, filename: str = "output.json") -> None:
    """
    Save output data to JSON file.
    """

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✅ Data saved to {filename}")

    except Exception as e:
        print(f"❌ Error saving JSON: {e}")