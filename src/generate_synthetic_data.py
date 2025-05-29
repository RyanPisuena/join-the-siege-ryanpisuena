import os
from openai import OpenAI
import json
import time

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create data directory if it doesn't exist
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

doc_types = {
    "invoice": "invoices",
    "bank_statement": "bank statements",
    "drivers_licence": "driver's licenses"
}

samples_per_type = 50 # to use in the prompt to generate the number per doc type

def generate_examples(doc_type_label, description):
    prompt = f"""
Generate {samples_per_type} examples of OCR-style extracted text from scanned {description}.
Each entry should look like 1–3 sentences of realistic, unstructured OCR output,
containing key fields typical of that document type.

Return the result as a Python list of strings with no extra commentary or formatting.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        raw_output = response.choices[0].message.content

        # Try to extract the list using eval safely
        examples = eval(raw_output.strip(), {"__builtins__": {}})
        if not isinstance(examples, list):
            raise ValueError("Invalid response format")
        return [(x, doc_type_label) for x in examples]
    except Exception as e:
        print(f"Failed for {doc_type_label}: {e}")
        return []


def main():
    all_data = []
    for label, desc in doc_types.items():
        print(f"Generating examples for: {label}")
        examples = generate_examples(label, desc)
        all_data.extend(examples)
        time.sleep(2)  # avoid rate limits

    # Save to disk for use in training
    output_file = os.path.join(DATA_DIR, "synthetic_data.json")
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=2)

    print(f"✅ Saved synthetic data to {output_file} with {len(all_data)} entries.")

if __name__ == "__main__":
    main()
