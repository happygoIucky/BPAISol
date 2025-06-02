#this demo is to split the dataset to chunk it as sometimes customer may have context length more than x2 or x3 requirement
#typically context window is controlled based on the model used thus chunking is necessary.
import os
import json
from byteplussdkarkruntime import Ark

# Generate a large JSON with many items (simulate >128k token case)
data = [{"id": i, "content": f"Example sentence number {i}. This might get long quickly."} for i in range(5000)]

# Helper: Estimate size and chunk it (naive token estimation: ~10 tokens per item)
chunk_size = 300  # Adjust based on your tokenizer
chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

# Init BytePlus Ark Client
client = Ark(yourapikey)

# Run through each chunk
for i, chunk in enumerate(chunks):
    chunk_json = json.dumps(chunk, indent=2)
    prompt = f"Please summarize the following chunk of data:\n{chunk_json}"

    completion = client.chat.completions.create(
        model="deepseek-r1-250120",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(f"\n--- Summary for Chunk {i + 1} ---")
    print(completion.choices[0].message.content)

    # Output token usage if available
    if hasattr(completion, 'usage'):
        print("\nToken Usage:")
        print(f"  Prompt tokens: {completion.usage.prompt_tokens}")
        print(f"  Completion tokens: {completion.usage.completion_tokens}")
        print(f"  Total tokens: {completion.usage.total_tokens}")
    else:
        print("Token usage info not available for this chunk.")