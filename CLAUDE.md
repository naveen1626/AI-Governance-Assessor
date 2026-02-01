# Project: AI Dual‑Use Risk Assessor for Research Papers

This `claude.md` is the main spec.  
Goal: Build a web tool that takes an **research paper** (URL or abstract text) and returns a **structured dual‑use risk assessment** plus **governance recommendations**.

Tool only analyzes **text** (titles, abstracts, model cards, or paper PDFs converted to text).

---

## 1. One‑Sentence Pitch

A web tool that ingests research papers (via URL or abstract text) and produces a structured dual‑use risk assessment plus suggested governance actions for research governance workflows.

---

## 2. High‑Level Behavior

### Inputs (two modes)

1. **URL mode**
   - User pastes a URL to a research paper (e.g., arXiv, conference PDF, company blog).
   - Backend:
     - Downloads the document (if accessible).
     - Extracts title + abstract (and possibly a short “methods” snippet).
     - If download or parsing fails, shows a clear error and suggests “paste abstract manually”.

2. **Abstract mode**
   - User pastes or types:
     - Paper title
     - Abstract (required)
     - Optional short “methods / contributions” summary.

Additional metadata fields (both modes):

- Intended dissemination:
  - “Internal only”
  - “Preprint / arXiv only”
  - “Conference / journal”
  - “Open‑source code + weights”
- Intended audience:
  - “Governance auditor”
  - “Broad developer community”
  - “Export control reviewer”

### Core idea

- **Normalize to a text “model card”**:
  - A single `ResearchCard` object containing title, abstract, optional snippet, and metadata.
- **Apply semiconductor‑specific dual‑use axes (C1–C4)** with a **0–3 rubric**.
- **Compute overall tier**: Low / Medium / High / Critical.
- **Emit governance recommendations**: e.g., “OK to publish”, “Needs export‑control review”, “Internal‑use only”.

---

## 3. Risk Axes & Rubric (Semiconductor Focus)

We reuse the axis definitions, but clarify that they apply to **research papers** (not just tools).

### 3.1 Axes

get the data from existing "Dual use risk evaluation framework.docx" for axes frameworks for identified research category or generate axes using a llm 

example for semiconductor  
**C1 – Advanced accelerator design help**  
“Does this research materially help design or optimize high‑end AI accelerators or other chips that might be export‑controlled?”

**C2 – Export‑control circumvention potential**  
“Does this research help achieve near‑frontier performance at older nodes / circumvent compute or export thresholds?”

**C3 – Military / intelligence applications**  
“Is it aimed at, or obviously applicable to, defense, surveillance, SIGINT, or weapons systems?”

**C4 – Expertise‑reduction / democratization**  
“Does it significantly lower the expertise needed to design or tape‑out advanced chips (e.g., novice‑friendly EDA copilots, templates, or automated flows)?”

### 3.2 Scoring rubric per axis (0–3)

For each axis, on **title + abstract + snippet**:

- **0** – Not relevant / clearly benign.  
- **1** – Weak signal, indirect help only.  
- **2** – Meaningful assistance but still requires strong expert context.  
- **3** – Strong, direct assistance that substantially lowers barriers for concerning uses.

Implementation detail:

- LLM‑based scoring

---

## 4. Overall Tier & Governance Actions

### 4.1 Tier rules

Use axis scores (C1–C4) + dissemination / audience metadata:

- **Low**: all axes ≤ 1.
- **Medium**: any axis = 2, none = 3.
- **High**:
  - Any axis = 3, but intended audience experts on the research fields
- **Critical**:
  - Any axis = 3 **and** dissemination or audience indicates broad/open access:
    - Intended audience includes “General AI researchers” or “Broad developer community”.
    - OR dissemination is “Open‑source code + weights” or clearly “public GitHub repo”.

### 4.2 Governance actions

- **Low**:
  - “Proceed, no special review.”
- **Medium**:
  - “Record assessment in internal tracking.”
  - “Internal governance review recommended before public release.”
- **High**:
  - “Export‑control / national‑security review before any external release.”
  - “Default to internal‑only preprint or limited distribution until reviewed.”
- **Critical**:
  - “Default no open release (code/weights/methods).”
  - “Escalate to governance / export‑control committee.”
  - “Consider red‑teaming and structured risk mitigation before any publication.”

---

