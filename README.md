# multi-llm

#  Hybrid Multi-Agent LLM System with Iterative Refinement & Benchmark Evaluation

##  Overview

This project implements a **Hybrid Multi-Agent Large Language Model (LLM) System** that collaboratively solves complex problems using multiple AI agents.

Unlike traditional single-model systems, this framework enables:
- Multi-perspective solution generation
- Iterative refinement through feedback
- Hybrid evaluation using LLM + rule-based scoring
- Benchmark testing using MMLU

---

##  Key Idea

Instead of relying on a single model:

```

One LLM ❌
→ Multiple Agents ✅
→ Collaboration + Feedback ✅
→ Self-improving System 🔥

```

---

##  System Architecture

```

User Problem
↓
Multi-Agent Generation (A, B, C)
↓
Cross-Agent Review
↓
Revision with Feedback
↓
Judge Evaluation
↓
Decision (Iterate / Stop)

```

---

##  Agents

| Agent | Role | Model |
|------|------|------|
| A | Technical Specialist | LM Studio (Mistral) |
| B | Creative Innovator | Hugging Face (LLaMA) |
| C | Strategic Thinker | Hugging Face (Zephyr) |

---

##  Features

### ✅ 1. Multi-Agent Collaboration
- Each agent generates different perspectives
- Improves diversity and quality of solutions

---

### ✅ 2. Iterative Refinement Loop

```

Generate → Review → Revise → Judge → Iterate

```

- Agents critique each other
- Solutions improve over iterations

---

### ✅ 3. Hybrid Scoring System

Combines:
- LLM-based evaluation
- Rule-based checklist scoring

```

Final Score = 0.7 × LLM Score + 0.3 × Checklist Score

```

---

### ✅ 4. Score Normalization

- Converts scores into percentages
- Enables fair comparison between agents

---

### ✅ 5. Robust JSON Handling

Handles:
- Invalid JSON outputs
- Markdown cleanup
- Nested JSON extraction

---

### ✅ 6. Best Solution Extraction

```

Evaluate → Select Best Agent → Return Best Solution

```

---

## ⚙️ Dual Mode System

---

### 🔹 Normal Mode (Reasoning Mode)

Used for complex problems:

```

Generate → Review → Revise → Judge → Iterate

```

✔ Deep reasoning  
✔ High-quality structured solutions  

---

### 🔹 MCQ Mode (Benchmark Mode)

Used for MMLU evaluation:

```

Generate → Extract Answers → Confidence-Based Selection

```

✔ Fast execution  
✔ Format-compliant output  
✔ Avoids incorrect majority bias  

---

## 📊 Benchmark: MMLU Evaluation

### 🧪 What is MMLU?

Massive Multitask Language Understanding benchmark:
- Multiple subjects (math, reasoning, etc.)
- Multiple-choice questions

---

### 🔧 Evaluation Pipeline

```

MMLU Question
↓
Multi-Agent System (MCQ Mode)
↓
Answer Extraction (A/B/C/D)
↓
Comparison with Ground Truth
↓
Accuracy Calculation

```

---

### 📈 Results

| Stage | Accuracy |
|------|--------|
| Initial system | 20% |
| After fixes | 30% |
| After MCQ redesign | ~50–70% (expected) |

---

### 🧠 Key Insight

Low initial accuracy was due to:

```

Mismatch between reasoning pipeline and MCQ evaluation ❌

```

Solved by:

```

Separate lightweight MCQ pipeline ✅

```

---

## 🧪 Example Output

- Multi-iteration improvement observed
- Agent A frequently selected as best
- Hybrid + normalized scores used for decision

---

## 🛠️ Tech Stack

- **Python**
- **LM Studio** (local LLM inference)
- **Hugging Face API**
- **Datasets library** (MMLU)
- **JSON parsing & regex**
- **LangChain (optional integration)**

---

## 📂 Project Structure

```

multi_llm_main/
│
├── multi_llm.py       # Core multi-agent system
├── benchmark.py      # MMLU evaluation
├── memory.json       # Run history
├── .env              # API keys
└── README.md

````

---

## ▶️ How to Run

### 1️⃣ Install dependencies
```bash
pip install datasets python-dotenv
````

---

### 2️⃣ Run main system

```bash
python multi_llm.py
```

---

### 3️⃣ Run benchmark

```bash
python benchmark.py
```

---

## ⚠️ Challenges Faced

| Problem                 | Solution                   |
| ----------------------- | -------------------------- |
| Invalid JSON            | Custom parser              |
| API mismatch            | Correct endpoints          |
| Low accuracy            | MCQ-specific pipeline      |
| Wrong answer extraction | Regex + JSON parsing       |
| Majority voting errors  | Confidence-based selection |

---

## 🔮 Future Work

Future work will focus on extending the system towards **Deep Agent architectures**, where agents can learn from past interactions, adapt their roles dynamically, and improve decision-making over time.

---

## 🧠 Key Contributions

* Multi-agent collaborative LLM system
* Iterative self-improving pipeline
* Hybrid scoring mechanism
* Dual-mode execution (reasoning + benchmark)
* MMLU benchmark integration

---

## 🗣️ Final Insight

> This project transforms LLM usage from a single-pass generation system into a collaborative, self-improving, and benchmark-evaluated AI framework.

---


