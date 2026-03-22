from datasets import load_dataset
import re
from multi_llm import orchestration_loop

# Load dataset
dataset = load_dataset("cais/mmlu", "all", split="test")

# Use small sample (start small)
sample = dataset.select(range(10))


def format_question(q, choices):
    options = "\n".join(
        [f"{chr(65+i)}) {c}" for i, c in enumerate(choices)]
    )
    return f"{q}\n{options}"

def extract_option(text):
    import json
    import re

    if not text:
        return None

    text = str(text)

    # ✅ Try JSON parsing first
    try:
        data = json.loads(text)
        if "answer" in data:
            return data["answer"]
    except:
        pass

    # ✅ Try extracting from JSON-like string
    match = re.search(r'"answer"\s*:\s*"?([A-D])"?', text)
    if match:
        return match.group(1)

    # ✅ Fallback: plain A/B/C/D
    match = re.search(r'\b[A-D]\b', text)
    if match:
        return match.group(0)

    return None


score = 0

for i, item in enumerate(sample):
    print(f"\n=== QUESTION {i+1} ===")

    question = format_question(item["question"], item["choices"])

    print("Question:\n", question)

    # Run your system in MCQ mode
    result = orchestration_loop(question, max_iter=0, mode="mcq")

    best_solution = str(result.get("best_solution", "")).strip()



    print("\nModel Output:\n", best_solution)

    pred = extract_option(str(best_solution))
    correct = chr(65 + item["answer"])

    print(f"Predicted: {pred}, Correct: {correct}")

    if pred == correct:
        score += 1

accuracy = score / len(sample)
print("\n✅ FINAL ACCURACY:", accuracy)
