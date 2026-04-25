# main.py

import time

from agent.fetcher import fetch_article
from agent.processor import (
    clean_text,
    validate_text,
    chunk_text,
    select_representative_chunks
)

from agent.extractor import (
    process_chunk_with_ai,
    aggregate_results
)

from utils.json_handler import format_output, save_to_json
from utils.webhook import send_webhook


def run_pipeline(url: str):
    start_time = time.time()

    try:
        # 1. Fetch
        article_text = fetch_article(url)

        # 2. Clean + Validate
        cleaned_text = clean_text(article_text)

        if not validate_text(cleaned_text):
            raise Exception("Invalid content")

        # 3. Chunking
        chunks = chunk_text(cleaned_text)

        # 4. Smart selection
        selected_chunks = select_representative_chunks(chunks)

        # 5. AI processing
        chunk_results = [
            process_chunk_with_ai(chunk)
            for chunk in selected_chunks
        ]

        # 6. Aggregation
        final_result = aggregate_results(chunk_results)

        processing_time = round(time.time() - start_time, 2)

        # 7. Output
        output = format_output(
            url=url,
            summary=final_result.get("summary", []),
            technologies=final_result.get("technologies", []),
            status="success",
            processing_time=processing_time,
            chunks_used=len(selected_chunks)
        )

    except Exception as e:
        output = format_output(
            url=url,
            summary=[],
            technologies=[],
            status=f"failed: {str(e)}"
        )

    # 8. Save + webhook
    save_to_json(output)
    send_webhook(output)


if __name__ == "__main__":
    test_url = "https://www.ibm.com/think/topics/artificial-intelligence"
    run_pipeline(test_url)