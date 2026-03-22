# multi_llm.py
"""
Multi-LLM collaboration runner using:
- LLM1: Groq via langchain_groq.ChatGroq
- LLM2: Google Gemini via google.generativeai
- LLM3: OpenRouter (OpenAI-compatible client) via openai.OpenAI

Flow:
User -> TaskDistributor -> LLM1/LLM2/LLM3 -> Collector -> ReviewDistributor ->
 each reviewer reviews two others -> Feedback -> Revision -> Final Collector -> Judge -> Iterate
"""

import os
import time
import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, Any
from dotenv import load_dotenv

# LLM clients
#from langchain_groq import ChatGroq
#from langchain.prompts import ChatPromptTemplate
#import google.generativeai as genai
#from openai import OpenAI as OpenRouterClient  # openrouter-compatible client

from openai import OpenAI
from huggingface_hub import InferenceClient
import threading


load_dotenv()

# -------------------------
# Config
# -------------------------



MAX_ITER = 3
QUALITY_THRESHOLD = 70  # for judge numeric interpretation
MEMORY_FILE = "memory.json"

# -------------------------
# Initialize clients
# -------------------------
# LM Studio client
lm_client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

# Hugging Face clients
hf_token = os.getenv("HF_TOKEN")

#print("HF TOKEN:", hf_token)

if not hf_token:
    raise ValueError("HF_TOKEN not found in .env file")

hf_client_1 = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=hf_token
)

hf_client_2 = InferenceClient(
    #model="microsoft/Phi-3-mini-4k-instruct",
    model="HuggingFaceH4/zephyr-7b-beta",
    token=hf_token
)

# -------------------------
# Data classes / memory
# -------------------------
@dataclass
class Artifact:
    role: str
    iteration: int
    text: str
    metadata: Dict[str, Any]

def append_memory(item: Artifact):
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
    except Exception as e:
        print("Warning: failed to write memory:", e)

# -------------------------
# MCQ Prompt Templates (for benchmarking)
# -------------------------
MCQ_TASK_PROMPT = {
    "A": lambda problem: (
        "Solve the MCQ step-by step internally.\n"
        f"{problem}\n\n"
        "IMPORTANT:\n"
        "Return STRICT JSON ONLY:\n"
        "{ \"answer\": \"A\" }\n"
        "Answer must be ONLY one letter: A, B, C, or D.\n"
        "No explanation."
    ),
    "B": lambda problem: (
        "Solve the MCQ carefully .\n"
        f"{problem}\n\n"
        "Return ONLY:\n"
        "{ \"answer\": \"A\" }\n"
        "No explanation."
    ),
    "C": lambda problem: (
        "Solve the MCQ.\n"
        f"{problem}\n\n"
        "STRICT:\n"
        "{ \"answer\": \"A\" }\n"
    ),
}

# -------------------------
# Prompt templates (structured JSON encouraged)
# -------------------------
TASK_PROMPT = {
    "A": lambda problem: (
        "You are LLM1  acting as a Technical Specialist.\n"
        "Produce a JSON object with keys: summary, assumptions, solution_steps, pseudocode, complexity.\n"
        f"Problem: {problem}\n"
        "Return only a valid JSON object (no extra commentary).\n"
        "STRICT RULES:\n"
        " - output must be valid json"
        " - no explianations"
        "-no markdown."
    ),
    "B": lambda problem: (
        "You are LLM2  acting as a Creative Innovator.\n"
        "Produce a JSON object with keys: summary, top_ideas (array), prototype_idea, tradeoffs.\n"
        f"Problem: {problem}\n"
        "Return only a valid JSON object (no extra commentary).\n"
        "STRICT RULES:\n"
        "- Output MUST be valid JSON\n"
        "- No explanations\n"
        "- No markdown\n"
    ),
    "C": lambda problem: (
        "You are LLM3 acting as a Strategic Thinker.\n"
        "Produce a JSON object with keys: summary, roadmap (ordered list), risks, kpis_timeline.\n"
        f"Problem: {problem}\n"
        "Return only a valid JSON object (no extra commentary).\n"
                    "STRICT RULES:\n"
            "- Output MUST be valid JSON\n"
            "- No explanations\n"
            "- No markdown\n"
    ),
}

REVIEW_PROMPT = lambda reviewer_role, sol_a, sol_b: (
    f"You are a reviewer (role={reviewer_role}). You will review two solutions A and B.\n"
    "For each solution produce a JSON object with keys: summary (one-liner), strengths (array), "
    "weaknesses (array), suggestions (array of prioritized actionable items).\n"
    "Return a JSON object {\"A\": {...}, \"B\": {...}} and nothing else.\n\n"
    f"Solution A:\n{sol_a}\n\nSolution B:\n{sol_b}\n"
)

REVISION_PROMPT = lambda owner_role, original, feedback: (
    f"You are the owner ({owner_role}). Original solution: {original}\n"
    f"Feedback from reviewers:\n{feedback}\n"
    "Produce a JSON object {\"changes_made\": [..], \"revised_solution\": {...}} where revised_solution "
    "matches the original solution schema. Return only JSON."
)

# JUDGE_PROMPT = lambda A, B, C, thr: (
#     "You are an objective judge. Given three revised solutions A, B, C (each JSON), score each from 0-100 "
#     "on correctness, feasibility, completeness. Return a JSON like:\n"
#     "{\"A\": {\"score\": int, \"reason\": str}, \"B\": {...}, \"C\": {...}, \"decision\": \"Good Enough\" or \"Needs Improvement\"}\n"
#     f"Threshold for Good Enough = {thr}\n\nA:\n{A}\n\nB:\n{B}\n\nC:\n{C}\n"
# )

#revised judge prompt
JUDGE_PROMPT = lambda A, B, C, thr: (
    "You are a strict evaluation judge.\n"
    "Evaluate three solutions A, B, C based on:\n"
    "1. Correctness\n"
    "2. Feasibility\n"
    "3. Completeness\n\n"

    "SCORING RULES:\n"
    "- Each criterion: 0 to 100\n"
    "- Final score = average of three\n"
    "- Be strict and realistic\n\n"

    "OUTPUT FORMAT (STRICT JSON ONLY):\n"
    "{\n"
    "  \"A\": {\"correctness\": int, \"feasibility\": int, \"completeness\": int, \"final_score\": int, \"reason\": str},\n"
    "  \"B\": {...},\n"
    "  \"C\": {...},\n"
    "  \"best_agent\": \"A or B or C\",\n"
    "  \"decision\": \"Good Enough\" or \"Needs Improvement\"\n"
    "}\n\n"

    f"Threshold for Good Enough = {thr}\n\n"
    f"A:\n{A}\n\nB:\n{B}\n\nC:\n{C}\n"
)


# -------------------------
# LLM call wrappers
# # -------------------------
def call_local_llm(prompt: str, timeout: int = 30) -> str:
    try:
        response = lm_client.chat.completions.create(
            model="mistralai/mistral-7b-instruct-v0.3",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[[Local LLM call failed: {e}]]"
    
def call_hf_llm_1(prompt: str, timeout: int = 30) -> str:
    try:
        response = hf_client_1.chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[[HF Model 1 call failed: {e}]]"
    
def call_hf_llm_2(prompt: str, timeout: int = 30) -> str:
    try:
        response = hf_client_2.chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[[HF Model 2 call failed: {e}]]"


# -------------------------
# Helpers: parse JSON or fallback (IMPROVED)
# -------------------------
def parse_json_or_text(s: str):
    if not s:
        return {"__raw": ""}

    s = s.strip()

    # Remove markdown ```json ``` if present
    s = re.sub(r"```json|```", "", s)

    # Try direct JSON first
    try:
        return json.loads(s)
    except Exception:
        pass

    # Improved: extract FULL JSON block using stack (handles nested JSON)
    def extract_full_json(text):
        stack = []
        start = -1

        for i, ch in enumerate(text):
            if ch == '{':
                if not stack:
                    start = i
                stack.append(ch)
            elif ch == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        return text[start:i+1]

        return None

    json_block = extract_full_json(s)

    if json_block:
        try:
            return json.loads(json_block)
        except Exception:
            pass

    # fallback
    return {"__raw": s}

# -------------------------
# Orchestrator (diagram logic)
# -------------------------
# def task_distributor(problem: str) -> Dict[str, str]:
#     return {agent: TASK_PROMPT[agent](problem) for agent in ("A", "B", "C")}

def task_distributor(problem: str, mode="normal") -> Dict[str, str]:
    if mode == "mcq":
        return {agent: MCQ_TASK_PROMPT[agent](problem) for agent in ("A", "B", "C")}
    else:
        return {agent: TASK_PROMPT[agent](problem) for agent in ("A", "B", "C")}
    
def call_agent(agent: str, prompt: str) -> str:
    # Map agent to concrete call
    if agent == "A":
        return call_local_llm(prompt)
    elif agent == "B":
        return call_hf_llm_1(prompt)
    elif agent == "C":
        return call_hf_llm_2(prompt)
    else:
        raise ValueError("Unknown agent")

def collect_solutions(solutions: Dict[str, str], iteration: int):
    for a, txt in solutions.items():
        append_memory(Artifact(role=f"solution_{a}", iteration=iteration, text=txt, metadata={"agent": a}))

def review_distributor(solutions: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    # returns mapping reviewer -> {"sol1":..., "sol2":...}
    return {
        "A": {"sol1": solutions["B"], "sol2": solutions["C"]},
        "B": {"sol1": solutions["A"], "sol2": solutions["C"]},
        "C": {"sol1": solutions["A"], "sol2": solutions["B"]},
    }

def reviewer_call(reviewer: str, sol1: str, sol2: str) -> str:
    prompt = REVIEW_PROMPT(reviewer, sol1, sol2)
    return call_agent(reviewer, prompt)

def revision_call(agent: str, original: str, feedback_summary: str) -> str:
    prompt = REVISION_PROMPT(agent, original, feedback_summary)
    return call_agent(agent, prompt)

# def judge_call(A: str, B: str, C: str) -> Dict[str, Any]:
#     prompt = JUDGE_PROMPT(A, B, C, QUALITY_THRESHOLD)
#     # Use Gemini (LLM2) as judge because it's good at structured responses in many cases
#     raw = call_hf_llm_1(prompt)
#     parsed = parse_json_or_text(raw)
#     return parsed

#revised judge call
def judge_call(A: str, B: str, C: str):
    prompt = JUDGE_PROMPT(A, B, C, QUALITY_THRESHOLD)

    raw = call_hf_llm_1(prompt)

    print("\n[Judge RAW OUTPUT]\n", raw)  # debug

    parsed = parse_json_or_text(raw)

    # fallback if parsing fails
    if "__raw" in parsed:
        return {
            "error": "Judge output not valid JSON",
            "raw": raw,
            "decision": "Needs Improvement"
        }

    return parsed


# def compute_decision(judge_result, threshold):
#     try:
#         scores = [
#             judge_result["A"]["final_score"],
#             judge_result["B"]["final_score"],
#             judge_result["C"]["final_score"],
#         ]
#         best_score = max(scores)

#         if best_score >= threshold:
#             return "Good Enough"
#         else:
#             return "Needs Improvement"
#     except Exception as e:
#         print("[decision error]", e)
#         return "Needs Improvement"

    
def checklist_score(solution: str):
    score = 0

    # solution = solution.lower()
    try:
        solution_text = json.dumps(parse_json_or_text(solution)).lower()
    except:
        solution_text = solution.lower()

    if "architecture" in solution:
        score += 20
    if "pseudocode" in solution:
        score += 20
    if "complexity" in solution:
        score += 20
    if "scalability" in solution:
        score += 20
    if "error" in solution or "failure" in solution:
        score += 20

    return score  # out of 100

def hybrid_score(agent_key, solution, judge_result):
    try:
        llm_score = judge_result[agent_key]["final_score"]
        rule_score = checklist_score(solution)

        # weighted combination
        final_score = 0.7 * llm_score + 0.3 * rule_score

        return final_score

    except Exception as e:
        print("[hybrid score error]", e)
        return 0
    

def compute_decision(judge_result, revised, threshold):
    try:
        scores = {}

        for agent in ["A", "B", "C"]:
            scores[agent] = hybrid_score(agent, revised[agent], judge_result)

        # 🔥 Normalize scores
        total = sum(scores.values())

        if total > 0:
            normalized_scores = {
                k: (v / total) * 100 for k, v in scores.items()
            }
        else:
            normalized_scores = scores

        print("\n[Hybrid Scores]", scores)
        print("[Normalized Scores]", normalized_scores)

        best_agent = max(normalized_scores, key=normalized_scores.get)
        best_score = normalized_scores[best_agent]

        if best_score >= threshold:
            return "Good Enough", best_agent
        else:
            return "Needs Improvement", best_agent

    except Exception as e:
        print("[decision error]", e)
        return "Needs Improvement", None
    


def orchestration_loop(problem: str, max_iter: int = MAX_ITER,mode="normal"):

    if mode == "mcq":
        print("[MCQ MODE] Running lightweight pipeline...")

        prompts = task_distributor(problem, mode="mcq")

        # generate only
        solutions = {}
        for agent in ["A", "B", "C"]:
            print(f"[gen] Agent {agent} generating...")
            solutions[agent] = call_agent(agent, prompts[agent])

        # extract answers directly
        answers = {}
        for agent in ["A", "B", "C"]:
            parsed = parse_json_or_text(solutions[agent])
            ans = parsed.get("answer", None)
            if isinstance(ans, str) and ans in ["A", "B", "C", "D"]:
                answers[agent] = ans

        # # majority voting
        # from collections import Counter
        # if answers:
        #     best_answer = Counter(answers.values()).most_common(1)[0][0]
        # else:
        #     best_answer = None
        # 🔥 choose best agent (confidence-based)

            confidence = {}
            valid_answers = {}

            for a in ("A", "B", "C"):
                parsed = parse_json_or_text(solutions[a])
                ans = parsed.get("answer", None)

                if isinstance(ans, str) and ans in ["A", "B", "C", "D"]:
                    valid_answers[a] = ans
                    confidence[a] = len(str(solutions[a]))  # longer = more confident

            print("[MCQ Answers]", valid_answers)

            if confidence:
                best_agent = max(confidence, key=confidence.get)
                best_answer = valid_answers[best_agent]
            else:
                best_answer = None

        return {
            "best_solution": {"answer": best_answer},
            "all_answers": answers
        }
    
    iteration = 0
    prompts = task_distributor(problem,mode)

    

    # initial generation
    solutions = {}
    for a in ("A", "B", "C"):
        print(f"[gen] Agent {a} generating...")
        sol = call_agent(a, prompts[a])
        solutions[a] = sol
        append_memory(Artifact(role=f"initial_{a}", iteration=iteration, text=sol, metadata={"agent": a}))
        time.sleep(0.2)

    collect_solutions(solutions, iteration)

    while True:
        iteration += 1
        print(f"\n=== ITERATION {iteration} ===")

        # Review stage
        rev_map = review_distributor(solutions)
        feedback_for = {"A": "", "B": "", "C": ""}
        for reviewer, pair in rev_map.items():
            print(f"[review] {reviewer} reviewing two solutions...")
            fb_raw = reviewer_call(reviewer, pair["sol1"], pair["sol2"])
            # attach the raw feedback to appropriate owners
            if reviewer == "A":
                feedback_for["B"] += f"\n[From A]\n{fb_raw}\n"
                feedback_for["C"] += f"\n[From A]\n{fb_raw}\n"
            elif reviewer == "B":
                feedback_for["A"] += f"\n[From B]\n{fb_raw}\n"
                feedback_for["C"] += f"\n[From B]\n{fb_raw}\n"
            elif reviewer == "C":
                feedback_for["A"] += f"\n[From C]\n{fb_raw}\n"
                feedback_for["B"] += f"\n[From C]\n{fb_raw}\n"
            append_memory(Artifact(role=f"feedback_from_{reviewer}", iteration=iteration, text=fb_raw, metadata={"reviewer": reviewer}))
            time.sleep(0.2)

        # Revision stage
        revised = {}
        for agent in ("A", "B", "C"):
            print(f"[revise] Agent {agent} revising with feedback...")
            rev_raw = revision_call(agent, solutions[agent], feedback_for[agent])
            revised[agent] = rev_raw
            append_memory(Artifact(role=f"revised_{agent}", iteration=iteration, text=rev_raw, metadata={"agent": agent}))
            time.sleep(0.2)

        # Final collect
        collect_solutions(revised, iteration)

        # Judge
        print("[judge] Evaluating revised solutions...")
        judge_result = judge_call(revised["A"], revised["B"], revised["C"])
        print("Judge raw/parsed:", json.dumps(judge_result, indent=2, ensure_ascii=False))
        

        # # Decide to stop based on judge_result
        # decision = None
        # # try structured decision field
        # if isinstance(judge_result, dict) and "decision" in judge_result:
        #     decision = judge_result["decision"]
        # else:
        #     # fallback: if any textual "Good Enough"
        #     raw_text = ""
        #     try:
        #         raw_text = judge_call(revised["A"], revised["B"], revised["C"])
        #     except Exception:
        #         raw_text = ""
        #     if isinstance(raw_text, str) and "Good Enough" in raw_text:
        #         decision = "Good Enough"
        # Compute decision using scores (NOT LLM text)

        #revised method for decision
        decision, best_agent = compute_decision(judge_result, revised, QUALITY_THRESHOLD)


        # 🔥 FIX 4: Handle invalid judge output
        if isinstance(judge_result, dict) and "error" in judge_result:
            print("[warning] Judge output invalid → using fallback")
            best_agent = "A"  # fallback to Agent A

        best_solution = revised.get(best_agent, None)

        print(f"[decision] {decision}")
        print(f"🏆 Best Agent: {best_agent}")
        # print("\n🏆 FINAL BEST SOLUTION:\n", best_solution)

        if decision == "Good Enough" or iteration >= max_iter:
            print("[done] Terminating loop.")

            best_solution = revised.get(best_agent, None)

            print("\n🏆 FINAL BEST SOLUTION:\n", best_solution)

            return {
                "final_solutions": revised,
                "best_agent": best_agent,
                "best_solution": best_solution,
                "iterations": iteration,
                "judge": judge_result
            }
        else:
            print("[loop] Not good enough yet, continue to next iteration.")
            solutions = revised
            continue

# -------------------------
# Run as script
# -------------------------
# if __name__ == "__main__":
#     print("=== Multi-LLM collaboration (Groq, Gemini, OpenRouter) ===")
#     user_problem = input("Enter the complex problem to solve: ").strip()
#     if not user_problem:
#         user_problem = ("Design a scalable notification system for a chat app that supports "
#                         "delivery guarantees, message ordering, and offline deliveries for millions of users.")
#     result = orchestration_loop(user_problem, max_iter=MAX_ITER)
#     print("\n=== FINAL OUTPUT (truncated) ===")
#     for k, v in result["final_solutions"].items():
#         print(f"\n--- Solution {k} (first 1000 chars) ---\n{v[:1000]}")
#     print("\nJudge result:\n", json.dumps(result["judge"], indent=2, ensure_ascii=False))
#     print("\nRun history appended to", MEMORY_FILE)

# -------------------------
# Run as script
# -------------------------
def run_cli():
    print("=== Multi-LLM collaboration ===")
    user_problem = input("Enter the complex problem to solve: ").strip()
    if not user_problem:
        user_problem = ("Design a scalable notification system for a chat app that supports "
                        "delivery guarantees, message ordering, and offline deliveries for millions of users.")
    result = orchestration_loop(user_problem, max_iter=MAX_ITER)
    print("\n=== FINAL OUTPUT (truncated) ===")
    for k, v in result["final_solutions"].items():
        print(f"\n--- Solution {k} (first 1000 chars) ---\n{v[:1000]}")
    print("\nJudge result:\n", json.dumps(result["judge"], indent=2, ensure_ascii=False))
    print("\nRun history appended to", MEMORY_FILE)

if __name__ == "__main__":
    run_cli()
