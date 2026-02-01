# AI Dual-Use Risk Assessor: An LLM-Powered Framework for Research Governance

## Abstract

The rapid advancement of artificial intelligence and frontier research across biomedical sciences, semiconductor technology, cybersecurity, chemistry, and nuclear domains presents unprecedented dual-use challenges for research governance. This paper presents the **AI Dual-Use Risk Assessor**, a web-based tool that leverages large language models (LLMs) to perform structured risk assessments of research papers across six high-risk domains. The system implements a universal 12-axis evaluation framework spanning capability assessment, accessibility analysis, safeguard evaluation, impact scope, uncertainty quantification, and regulatory alignment. By automatically detecting research categories and generating context-aware governance recommendations that reference domain-specific regulatory frameworks (EU AI Act, DURC Policy, Export Administration Regulations, Chemical Weapons Convention, etc.), the tool bridges the gap between research innovation and responsible governance. Evaluation across 60+ research papers demonstrates accurate category detection (>95%) and appropriate risk tiering aligned with established dual-use principles. The system provides research institutions, funding agencies, and governance bodies with an automated first-pass assessment capability that can scale to meet the growing volume of dual-use research requiring oversight.

**Keywords:** Dual-use research, AI governance, risk assessment, large language models, research ethics, export controls, biosecurity, responsible innovation

---

## 1. Introduction

### 1.1 The Dual-Use Dilemma

Scientific research increasingly produces knowledge and artifacts with significant potential for both beneficial applications and malicious misuse. This "dual-use" characteristic is particularly pronounced in six critical domains:

1. **Biomedical/Life Sciences**: CRISPR gene editing, gain-of-function research, synthetic biology
2. **Semiconductor/AI Hardware**: Advanced chip design, AI accelerators, EDA automation
3. **Artificial Intelligence/Machine Learning**: Large language models, autonomous systems, capability scaling
4. **Cybersecurity**: Vulnerability research, exploit development, adversarial techniques
5. **Chemistry/Materials Science**: Energetic materials, novel compound synthesis, precursor chemistry
6. **Nuclear/Radiological**: Enrichment technology, reactor design, radiation detection

Traditional governance approaches relying on manual expert review cannot scale to the volume of research being published. The arXiv repository alone receives over 20,000 submissions monthly, many with potential dual-use implications requiring assessment.

### 1.2 Contributions

This paper presents the AI Dual-Use Risk Assessor, making the following contributions:

1. **Universal 12-Axis Framework**: A domain-agnostic risk evaluation structure applicable across all six high-risk research categories, incorporating reverse-scored safeguard axes

2. **LLM-Powered Assessment Pipeline**: Automated scoring using large language models with robust JSON parsing and multi-provider support (Anthropic, OpenAI, Google, Groq, Together AI)

3. **Regulatory-Aware Recommendations**: Context-sensitive governance recommendations that reference specific regulatory frameworks relevant to each research domain

4. **Tiering System**: A four-level risk classification (Low, Medium, High, Critical) that considers both technical risk scores and dissemination/audience metadata

5. **Analytics Dashboard**: Comprehensive visualization of assessment trends, capability-safeguard gaps, and portfolio-level risk metrics

---

## 2. Related Work

### 2.1 Dual-Use Research Governance

The governance of dual-use research has evolved significantly since the 2004 Fink Report established frameworks for life sciences oversight. Key regulatory milestones include:

- **US DURC Policy (2012/2014)**: Established institutional review requirements for life sciences research of concern
- **Wassenaar Arrangement**: Multilateral export control regime covering dual-use technologies
- **EU AI Act (2024)**: Risk-based regulation of AI systems including high-risk categorization
- **US Executive Order 14110 (2023)**: Safety and security requirements for frontier AI systems

However, these frameworks primarily address post-hoc review rather than automated assessment at the point of research dissemination.

### 2.2 AI for Research Assessment

Prior work on AI-assisted research evaluation has focused on:

- **Peer review assistance**: Automated reviewer matching and plagiarism detection
- **Impact prediction**: Citation forecasting and attention metrics
- **Ethical screening**: Conflict of interest and methodology validation

Our work extends this to dual-use risk assessment, a domain requiring nuanced understanding of both technical capabilities and misuse pathways.

---

## 3. System Architecture

### 3.1 Overview

The AI Dual-Use Risk Assessor is implemented as a web application using FastAPI (Python) with a JavaScript frontend. The architecture follows a layered design:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │ Assessment UI   │  │     Analytics Dashboard          │   │
│  │ (index.html)    │  │     (dashboard.html)            │   │
│  └────────┬────────┘  └────────────────┬────────────────┘   │
└───────────┼────────────────────────────┼────────────────────┘
            │                            │
┌───────────┼────────────────────────────┼────────────────────┐
│           │       API Layer            │                     │
│  ┌────────▼────────┐  ┌────────────────▼────────────────┐   │
│  │ /api/assess     │  │ /api/dashboard/stats            │   │
│  │ /api/fetch-url  │  │ /api/dashboard/assessments      │   │
│  │ /api/history    │  │                                 │   │
│  └────────┬────────┘  └────────────────┬────────────────┘   │
└───────────┼────────────────────────────┼────────────────────┘
            │                            │
┌───────────┼────────────────────────────┼────────────────────┐
│           │     Service Layer          │                     │
│  ┌────────▼────────┐  ┌────────────────▼────────────────┐   │
│  │ Risk Scorer     │  │ Governance Service              │   │
│  │ (LLM Scoring)   │  │ (Tiering + Recommendations)     │   │
│  └────────┬────────┘  └────────────────┬────────────────┘   │
│           │                            │                     │
│  ┌────────▼────────┐  ┌────────────────▼────────────────┐   │
│  │ URL Parser      │  │ Storage Service                 │   │
│  │ (arXiv/PDF/HTML)│  │ (JSON Persistence)              │   │
│  └─────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────┐
│                  LLM Provider Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Anthropic│ │ OpenAI   │ │ Google   │ │Together  │       │
│  │ Claude   │ │ GPT-4    │ │ Gemini   │ │ Llama    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Models

The core data structures are implemented using Pydantic for validation:

**ResearchInput**: Captures paper metadata including title, abstract, optional methods snippet, dissemination intent, and target audience.

**RiskScores**: Dictionary mapping axis IDs to AxisScore objects, with methods for computing effective scores (applying reverse scoring for safeguard axes).

**Assessment**: Complete assessment record including input, scores, computed tier, LLM-generated recommendations, and metadata (timestamp, ID, detected category).

### 3.3 Input Processing

The system supports two input modes:

1. **URL Mode**: Automatic extraction of title and abstract from:
   - arXiv pages (BeautifulSoup parsing of abstract pages)
   - PDF documents (PyPDF text extraction from first 2 pages)
   - Generic HTML (heuristic selector matching for common patterns)

2. **Manual Mode**: Direct text entry of title, abstract, and optional methods section

---

## 4. The 12-Axis Risk Framework

### 4.1 Framework Design

The assessment framework evaluates research across 12 axes organized into 6 sections:

| Section | Axis | Name | Question | Scoring |
|---------|------|------|----------|---------|
| **A: Capability** | A1 | Dangerous Capability Focus | Does research enable CBRN, cyber attack, or surveillance capabilities? | Standard |
| | A2 | Operationalization of Harm | How directly does output help convert malicious intent into action? | Standard |
| **B: Accessibility** | B1 | Model/System Accessibility | How accessible are primary artifacts to non-experts? | Standard |
| | B2 | User Skill Requirement | How little domain expertise is needed to apply findings harmfully? | Standard |
| **C: Safeguards** | C1 | Built-in Technical Safeguards | Extent of alignment techniques, filters, monitoring, access controls? | **Reverse** |
| | C2 | Mitigation & Deployment Plan | How clear are staged release plans and risk mitigation strategies? | **Reverse** |
| **D: Impact** | D1 | Potential Physical/Societal Harm | Severity of worst-case impacts if misused at scale? | Standard |
| | D2 | Target Population & Equity | Could misuse disproportionately harm vulnerable populations? | Standard |
| **E: Uncertainty** | E1 | Uncertainty About Dual-Use Pathways | How much unresolved uncertainty about potential misuse? | Standard |
| | E2 | Scalability of Misuse | Could findings enable large-scale or automated harmful actions? | Standard |
| **F: Regulatory** | F1 | Export-Control Sensitivity | Do artifacts fall within export control categories? | Standard |
| | F2 | Regulatory Alignment | Alignment with EU AI Act, sectoral regulations, responsible AI principles? | Standard |

### 4.2 Scoring Rubric

Each axis is scored on a 0-3 scale:

- **0**: Not relevant / clearly benign / strong controls in place
- **1**: Weak signal, indirect concern, or minor gap
- **2**: Meaningful concern but mitigated by context or expertise requirements
- **3**: Strong, direct concern that substantially raises risk profile

### 4.3 Reverse Scoring

Safeguard axes (C1, C2) use reverse scoring where:
- Higher raw scores indicate **better** safeguards
- Effective score = 3 - raw score (for risk calculation)

This ensures that strong safeguards reduce overall risk tier while maintaining intuitive scoring (higher = better safeguards).

---

## 5. Risk Tiering and Governance

### 5.1 Tier Calculation

The system computes risk tiers using effective scores (after reverse scoring) combined with dissemination and audience metadata:

```python
def compute_tier(scores, dissemination, audience):
    max_score = scores.max_effective_score()
    is_broad_access = (dissemination == OPEN_SOURCE or
                       audience == DEVELOPERS)
    is_expert_only = (audience == EXPERTS)

    if max_score <= 1:
        return LOW
    elif max_score == 2:
        return MEDIUM
    elif max_score == 3:
        if is_broad_access:
            return CRITICAL
        elif is_expert_only:
            return HIGH
        else:
            return HIGH
```

### 5.2 Tier Definitions

| Tier | Criteria | Governance Actions |
|------|----------|-------------------|
| **Low** | All effective scores ≤ 1 | Proceed with publication; standard documentation |
| **Medium** | Any score = 2, none = 3 | Internal tracking; governance review before public release |
| **High** | Any score = 3, expert audience | Export-control review; internal-only until cleared |
| **Critical** | Score = 3 + broad access | No open release; escalate to committee; red-teaming required |

### 5.3 LLM-Generated Recommendations

Rather than static recommendations, the system generates context-aware governance actions by prompting the LLM with:

1. Paper title and abstract
2. Detected research category
3. Computed risk tier
4. High-risk axes and safeguard gaps
5. Relevant regulatory frameworks for the category

**Regulatory Framework Mappings:**

| Category | Key Regulations |
|----------|-----------------|
| Biomedical | DURC Policy, Select Agent Regulations, Cartagena Protocol, WHO Framework |
| Semiconductor | EAR, CHIPS Act, Wassenaar Arrangement, FDPR |
| AI/ML | EU AI Act, US EO 14110, NIST AI RMF, OECD Principles |
| Cybersecurity | Wassenaar (intrusion software), CFAA, NIS2 Directive |
| Chemistry | Chemical Weapons Convention, REACH, Australia Group |
| Nuclear | NRC Part 810, NPT, IAEA Safeguards, Nuclear Suppliers Group |

---

## 6. Implementation Details

### 6.1 LLM Integration

The system supports five LLM providers through a unified interface:

```python
async def call_llm(prompt: str) -> str:
    provider = settings.llm_provider
    if provider == "anthropic":
        return await call_anthropic(prompt)
    elif provider == "openai":
        return await call_openai(prompt)
    elif provider == "google":
        return await call_google(prompt)
    elif provider == "groq":
        return await call_groq(prompt)
    elif provider == "together":
        return await call_together(prompt)
```

Default configuration uses Together AI with Llama-3.3-70B-Instruct-Turbo for cost-effective assessment.

### 6.2 Robust Response Parsing

LLM responses are parsed with multiple fallback strategies:

1. **Direct JSON parsing** of response text
2. **Markdown extraction** (removing ```json blocks)
3. **Regex JSON extraction** (finding {...} patterns)
4. **Per-axis regex extraction** (extracting individual score/rationale pairs)
5. **Default scores** with error messages (graceful degradation)

### 6.3 Dashboard Analytics

The analytics dashboard computes:

- **Risk Distribution**: Count per tier with percentage calculations
- **Category Distribution**: Papers per research category
- **Axis Averages**: Mean effective score per axis
- **Section Averages**: Aggregated section-level metrics
- **Capability Index**: Average of capability axes (A1, A2, D1, D2)
- **Safeguard Index**: Average of safeguard axes (C1, C2, F1, F2)
- **Governance Gap**: Capability Index - Safeguard Index
- **Trend Data**: Time-series of assessments over 30 days

---

## 7. Evaluation

### 7.1 Category Detection Accuracy

Testing across 60+ research papers spanning all six categories:

| Category | Papers Tested | Correct Detection | Accuracy |
|----------|---------------|-------------------|----------|
| Biomedical | 15 | 15 | 100% |
| Semiconductor | 12 | 11 | 92% |
| AI/ML | 14 | 14 | 100% |
| Cybersecurity | 10 | 10 | 100% |
| Chemistry | 5 | 5 | 100% |
| Nuclear | 6 | 5 | 83% |
| **Total** | **62** | **60** | **97%** |

### 7.2 Tier Appropriateness

Manual review of tier assignments against expert judgment:

- **Gain-of-function influenza research**: Correctly assigned HIGH tier with A1=3, D1=3
- **Advanced chip fabrication**: Correctly assigned HIGH with export control flags (F1=2)
- **Autonomous targeting systems**: Correctly assigned CRITICAL with open-source dissemination
- **Benign ML methodology papers**: Correctly assigned LOW tier

### 7.3 Recommendation Quality

LLM-generated recommendations successfully reference:
- Domain-specific regulations (e.g., DURC Policy for biomedical)
- Specific compliance actions (e.g., "Implement access controls per Select Agent Regulations")
- Appropriate escalation paths (e.g., "Escalate to export-control committee")

---

## 8. Discussion

### 8.1 Limitations

1. **LLM Reliability**: Scoring depends on LLM interpretation; different models may produce varying scores
2. **Abstract-Only Assessment**: Full-text analysis would provide more accurate risk evaluation
3. **Static Regulatory Mapping**: Regulations evolve; mappings require periodic updates
4. **No Adversarial Testing**: System has not been evaluated against deliberately misleading abstracts

### 8.2 Future Work

1. **Full-Text Analysis**: Integrate PDF parsing for complete paper analysis
2. **Expert Calibration**: Collect expert assessments to fine-tune scoring
3. **Multi-Model Ensemble**: Aggregate scores from multiple LLMs for robustness
4. **Regulatory API Integration**: Real-time lookup of current export control lists
5. **Institutional Integration**: APIs for integration with research management systems

### 8.3 Ethical Considerations

The system is designed as a **decision-support tool**, not a replacement for human judgment. Final governance decisions should involve:
- Domain expert review for HIGH/CRITICAL tiers
- Institutional review board oversight
- Legal/compliance consultation for export-controlled research

---

## 9. Conclusion

The AI Dual-Use Risk Assessor demonstrates that large language models can provide valuable automated first-pass assessment of dual-use research risks. By implementing a universal 12-axis framework with reverse-scored safeguard axes, the system captures both risk factors and mitigating controls. The integration of regulatory framework awareness enables context-specific governance recommendations that reference applicable laws and guidelines.

As research output continues to accelerate across high-risk domains, automated assessment tools will become increasingly important for maintaining effective governance without creating bottlenecks that impede beneficial research. The open architecture and multi-provider LLM support ensure the system can evolve with advancing AI capabilities while remaining accessible to institutions with varying resource constraints.

---

## References

1. National Research Council. (2004). *Biotechnology Research in an Age of Terrorism*. National Academies Press.

2. European Parliament. (2024). *Regulation (EU) 2024/1689 on Artificial Intelligence (AI Act)*.

3. White House. (2023). *Executive Order 14110 on Safe, Secure, and Trustworthy Development and Use of Artificial Intelligence*.

4. NIST. (2023). *AI Risk Management Framework (AI RMF 1.0)*.

5. Wassenaar Arrangement. (2023). *List of Dual-Use Goods and Technologies and Munitions List*.

6. US Department of Health and Human Services. (2014). *United States Government Policy for Institutional Oversight of Life Sciences Dual Use Research of Concern*.

7. OECD. (2019). *Recommendation of the Council on Artificial Intelligence*.

8. G7. (2023). *Hiroshima Process International Code of Conduct for Organizations Developing Advanced AI Systems*.

---

## Appendix A: System Requirements

- Python 3.10+
- FastAPI, Uvicorn
- Pydantic, httpx, BeautifulSoup4, PyPDF
- LLM API access (Anthropic, OpenAI, Google, Groq, or Together AI)

## Appendix B: Configuration

```env
LLM_PROVIDER=together
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
TOGETHER_API_KEY=your_api_key_here
```

## Appendix C: API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/assess` | POST | Submit paper for assessment |
| `/api/fetch-url` | POST | Extract title/abstract from URL |
| `/api/history` | GET | List all assessments |
| `/api/history/{id}` | GET | Get specific assessment |
| `/api/dashboard/stats` | GET | Get filtered statistics |
| `/api/dashboard/assessments` | GET | Get filtered assessment list |

---

*Project Repository: AI_Governance*
*License: MIT*
*Contact: [Institution Contact]*
