# AI Dual-Use Risk Assessor

An LLM-powered framework for automated dual-use risk assessment of research papers across six high-risk domains.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

## Overview

The AI Dual-Use Risk Assessor is a web-based tool that leverages large language models to perform structured risk assessments of research papers. It implements a universal 12-axis evaluation framework and generates context-aware governance recommendations referencing domain-specific regulatory frameworks.

### Key Features

- **Universal 12-Axis Framework**: Evaluates research across Capability, Accessibility, Safeguards, Impact, Uncertainty, and Regulatory dimensions
- **Multi-Category Support**: Biomedical, Semiconductor, AI/ML, Cybersecurity, Chemistry, Nuclear
- **Automatic Category Detection**: LLM-based classification of research domains
- **Regulatory-Aware Recommendations**: References EU AI Act, DURC Policy, Export Controls, and more
- **Risk Tiering**: Four-level classification (Low, Medium, High, Critical)
- **Analytics Dashboard**: Portfolio-level risk visualization and trends
- **Multi-Provider LLM Support**: Anthropic, OpenAI, Google, Groq, Together AI

## Quick Start

### Prerequisites

- Python 3.10 or higher
- An API key from one of: Together AI, OpenAI, Anthropic, Google, or Groq

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AI_Governance.git
cd AI_Governance

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API key
cp .env.example .env
# Edit .env and add your API key
```

### Configuration

Edit `.env` file:

```env
LLM_PROVIDER=together
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
TOGETHER_API_KEY=your_api_key_here
```

### Running the Application

```bash
python run.py
```

Open http://localhost:8000 in your browser.

## Usage

### Web Interface

1. **Assess a Paper**:
   - Paste a URL (arXiv, PDF, or HTML) or enter title/abstract manually
   - Select dissemination intent and target audience
   - Click "Assess" to get risk scores and recommendations

2. **View Dashboard**:
   - Navigate to http://localhost:8000/dashboard
   - Filter by date, category, or risk tier
   - View portfolio-level analytics

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/assess` | POST | Submit paper for assessment |
| `/api/fetch-url` | POST | Extract title/abstract from URL |
| `/api/history` | GET | List all assessments |
| `/api/history/{id}` | GET | Get specific assessment |
| `/api/dashboard/stats` | GET | Get filtered statistics |
| `/api/dashboard/assessments` | GET | Get filtered assessment list |

### Example API Call

```python
import requests

response = requests.post("http://localhost:8000/api/assess", json={
    "title": "Your Paper Title",
    "abstract": "Your paper abstract...",
    "dissemination": "Preprint / arXiv only",
    "audience": "Broad developer community"
})

assessment = response.json()
print(f"Risk Tier: {assessment['tier']}")
print(f"Recommendations: {assessment['recommendations']}")
```

## The 12-Axis Framework

| Section | Axis | Description |
|---------|------|-------------|
| **A: Capability** | A1, A2 | Dangerous capability focus, operationalization of harm |
| **B: Accessibility** | B1, B2 | Model accessibility, user skill requirements |
| **C: Safeguards** | C1*, C2* | Built-in safeguards, mitigation plans |
| **D: Impact** | D1, D2 | Physical/societal harm, vulnerable populations |
| **E: Uncertainty** | E1, E2 | Dual-use pathway uncertainty, scalability |
| **F: Regulatory** | F1, F2 | Export control sensitivity, regulatory alignment |

*Reverse-scored: Higher scores indicate better safeguards (lower risk)

## Project Structure

```
AI_Governance/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic data models
│   ├── routes/
│   │   ├── assess.py        # Assessment endpoint
│   │   ├── dashboard.py     # Dashboard analytics
│   │   ├── fetch.py         # URL fetching
│   │   └── history.py       # Assessment history
│   ├── services/
│   │   ├── risk_scorer.py   # LLM scoring logic
│   │   ├── governance.py    # Tier calculation & recommendations
│   │   ├── storage.py       # JSON persistence
│   │   └── url_parser.py    # URL content extraction
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Main assessment UI
│       └── dashboard.html   # Analytics dashboard
├── data/
│   ├── axes.json            # 12-axis framework config
│   └── assessments.json     # Stored assessments
├── tests/
│   └── test_multi_category_assessments.py
├── requirements.txt
├── run.py
├── .env.example
└── README.md
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs and issues
- 💡 Suggest new features or improvements
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🧪 Add test cases
- 🌐 Add support for new LLM providers

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{ai_dual_use_risk_assessor,
  title = {AI Dual-Use Risk Assessor: An LLM-Powered Framework for Research Governance},
  year = {2026},
  url = {https://github.com/YOUR_USERNAME/AI_Governance}
}
```

## Acknowledgments

- Developed during the [Apart Research Technical AI Governance Challenge](https://apartresearch.com/)
- Built with [FastAPI](https://fastapi.tiangolo.com/), [Tailwind CSS](https://tailwindcss.com/), and [Together AI](https://together.ai/)

## Contact

- Create an [issue](https://github.com/YOUR_USERNAME/AI_Governance/issues) for bug reports or feature requests
- Join discussions in [Discussions](https://github.com/YOUR_USERNAME/AI_Governance/discussions)
