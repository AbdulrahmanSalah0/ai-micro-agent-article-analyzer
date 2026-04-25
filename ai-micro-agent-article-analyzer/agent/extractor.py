# agent/extractor.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils.json_handler import deduplicate_technologies
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def process_chunk_with_ai(chunk: str) -> dict:
    """
    Process one chunk → summary + technologies
    """

    prompt = f"""
You are an expert AI technical analyst.

Task:
1. Summarize into exactly 3 bullet points
2. Extract technologies

Return ONLY valid JSON:

{{
  "summary": ["", "", ""],
  "technologies": []
}}

Text:
{chunk}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON generator. Always return valid JSON only."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except:
        return {"summary": [], "technologies": []}


def aggregate_results(results: list) -> dict:
    """
    Combine chunk outputs into final result.
    """

    all_summaries = []
    all_techs = []

    # 🔥 FIX: no json.loads here
    for r in results:
        all_summaries.extend(r.get("summary", []))
        all_techs.extend(r.get("technologies", []))

    unique_techs = deduplicate_technologies(all_techs)

    final_prompt = f"""
You are a senior AI system.

Refine the following into:
- EXACTLY 3 final bullet points
- Clean list of technologies (no duplicates)

Summaries:
{all_summaries}

Technologies:
{unique_techs}

Return ONLY JSON:

{{
  "summary": ["", "", ""],
  "technologies": []
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You output clean valid JSON only."
            },
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except:
        return {
            "summary": all_summaries[:3],
            "technologies": unique_techs
        }