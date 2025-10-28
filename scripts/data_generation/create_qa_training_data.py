"""
Enhanced Training Data Generator for SFSU Chatbot
Creates ChatGPT-quality Question-Answer pairs from raw scraped data

This uses Groq LLM to intelligently extract Q&A pairs from documents
"""

import json
import os
from groq import Groq
from dotenv import load_dotenv
import time

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_qa_pairs(document, max_pairs=5):
    """
    Use LLM to extract intelligent Q&A pairs from a document.
    This creates ChatGPT-quality training data.
    """

    content = document.get('content', '')
    title = document.get('title', '')
    url = document.get('url', '')
    category = document.get('category', '')

    if not content or len(content) < 100:
        return []

    # Truncate very long documents
    if len(content) > 4000:
        content = content[:4000] + "..."

    prompt = f"""You are an expert at creating training data for AI chatbots.

Given this SFSU webpage content, extract 3-5 high-quality Question-Answer pairs that students might ask.

Title: {title}
Category: {category}
URL: {url}

Content:
{content}

Instructions:
1. Create realistic questions students would actually ask
2. Questions should be specific and varied (who, what, where, when, how, why)
3. Answers should be comprehensive but concise (2-4 sentences)
4. Include specific details from the content (deadlines, requirements, contact info, URLs)
5. Make questions natural and conversational

Output ONLY valid JSON in this exact format:
[
  {{
    "question": "How do I apply for the CS graduate program?",
    "answer": "To apply for the SFSU CS graduate program, you need to submit...",
    "category": "{category}",
    "source_url": "{url}"
  }}
]

Generate the JSON now:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Creative but controlled
            max_tokens=2000,
            timeout=30
        )

        result = response.choices[0].message.content.strip()

        # Extract JSON from response (in case there's extra text)
        if '```json' in result:
            result = result.split('```json')[1].split('```')[0].strip()
        elif '```' in result:
            result = result.split('```')[1].split('```')[0].strip()

        qa_pairs = json.loads(result)

        print(f"   [OK] Extracted {len(qa_pairs)} Q&A pairs from: {title[:50]}...")
        return qa_pairs

    except json.JSONDecodeError as e:
        print(f"   [ERROR] JSON parsing error for {title[:50]}: {e}")
        print(f"   Response was: {result[:200]}")
        return []
    except Exception as e:
        print(f"   [ERROR] Error processing {title[:50]}: {e}")
        return []

def process_all_documents(input_files, output_file="data/qa_training_data.json"):
    """
    Process all documents and create Q&A training data.
    """

    all_qa_pairs = []

    for input_file in input_files:
        print(f"\n[FILE] Processing: {input_file}")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            print(f"   Found {len(documents)} documents")

            for i, doc in enumerate(documents):
                print(f"   [{i+1}/{len(documents)}] Processing: {doc.get('title', 'Untitled')[:40]}...")

                qa_pairs = extract_qa_pairs(doc)
                all_qa_pairs.extend(qa_pairs)

                # Rate limiting - don't overwhelm Groq API
                time.sleep(1)

                # Save progress every 10 documents
                if (i + 1) % 10 == 0:
                    print(f"   [SAVE] Saving progress... ({len(all_qa_pairs)} Q&A pairs so far)")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"   [ERROR] Error with file {input_file}: {e}")
            continue

    # Final save
    print(f"\n[COMPLETE] Generated {len(all_qa_pairs)} Q&A pairs")
    print(f"[SAVE] Saving to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)

    # Print sample
    if all_qa_pairs:
        print("\n[SAMPLE] Sample Q&A Pairs:")
        for qa in all_qa_pairs[:3]:
            print(f"\nQ: {qa['question']}")
            print(f"A: {qa['answer'][:100]}...")

    return all_qa_pairs

if __name__ == "__main__":
    print("[AI] SFSU Training Data Generator")
    print("=" * 60)
    print("This will create ChatGPT-quality Q&A pairs from your data\n")

    # Process the most important files first
    priority_files = [
        "data/ultimate_cs_general.json",
        "data/ultimate_cs_graduate.json",
        "data/ultimate_international_general.json",
        "data/ultimate_financial_aid.json",
        "data/ultimate_admissions_graduate.json",
        "data/ultimate_registrar_general.json",
    ]

    # Filter to only existing files
    existing_files = [f for f in priority_files if os.path.exists(f)]

    print(f"[FILES] Will process {len(existing_files)} files:")
    for f in existing_files:
        print(f"   - {f}")

    print("\n[WARNING] This will take ~10-15 minutes depending on file sizes")
    print("[WARNING] Uses Groq API (make sure you have credits)\n")

    input("Press Enter to start...")

    qa_pairs = process_all_documents(existing_files)

    print(f"\n[SUCCESS] Created {len(qa_pairs)} Q&A training pairs")
    print("[FILE] Saved to: data/qa_training_data.json")
    print("\n[NEXT] Upload this to your database for better responses!")
