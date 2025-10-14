import argparse
import json
from eval_graphrag import load_queries_from_json, longest_common_continuous_substring

def evaluate(ans_json, result_json):
    queries, answers, video_names = load_queries_from_json(ans_json)

    with open(result_json, "r", encoding="utf-8") as f:
        graphrag_results = json.load(f)

    correct, total = 0, len(queries)
    errors = []

    for i, query in enumerate(queries):
        ans_text = answers[i]
        preds = [item["source"] for item in graphrag_results if item["query"] == query]

        if not preds:
            print(f"No prediction found for query: {query}")
            errors.append(query)
            continue

        found = False
        for pred in preds:
            lcs = longest_common_continuous_substring(ans_text, pred)
            if lcs >= 30:
                found = True
                break

        if found:
            correct += 1
        else:
            errors.append(query)
            
    accuracy = correct / total if total > 0 else 0
    return {"total": total, "correct": correct, "accuracy": accuracy, "errors": errors}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ans", required=True, help="標準答案 JSON")
    parser.add_argument("--result", required=True, help="GraphRAG local search 結果 JSON")
    args = parser.parse_args()

    stats = evaluate(args.ans, args.result)
    print(f"Total: {stats['total']}, Correct: {stats['correct']}, Accuracy: {stats['accuracy']:.2%}")

    if stats["errors"]:
        print("\nThese queries did not match any correct segment:")
        for q in stats["errors"]:
            print("  -", q)
