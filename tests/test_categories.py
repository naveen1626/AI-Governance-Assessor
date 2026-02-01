"""
Test file for universal risk assessment framework.
Tests all research categories with sample papers using the 12-axis universal framework.

Run with: python -m pytest tests/test_categories.py -v
Or run directly: python tests/test_categories.py
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Universal axes (A1-F2)
EXPECTED_AXES = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2"]

# Sample papers for each category
TEST_PAPERS = {
    "biomedical": {
        "title": "CRISPR-Cas9 Gene Editing for Treating Sickle Cell Disease",
        "abstract": """This study presents a novel CRISPR-Cas9 approach for treating sickle cell disease
        by correcting the point mutation in the HBB gene. We demonstrate successful in vitro correction
        in patient-derived hematopoietic stem cells with minimal off-target effects. The edited cells
        showed restored hemoglobin production and normal red blood cell morphology. Our findings suggest
        a promising therapeutic avenue for this debilitating genetic disorder.""",
        "dissemination": "Conference / journal",
        "audience": "Domain experts only"
    },
    "semiconductor": {
        "title": "A Deep Reinforcement Learning Approach for Global Routing in VLSI Design",
        "abstract": """Global routing is a critical step in VLSI physical design that determines wire
        paths connecting circuit components. This paper presents a deep reinforcement learning method
        for solving the global routing problem. Our approach uses a policy gradient algorithm to learn
        optimal routing strategies from training on diverse circuit layouts. Experiments show our method
        achieves 15% improvement in wire length and 20% reduction in routing congestion compared to
        traditional algorithms on benchmark circuits.""",
        "dissemination": "Preprint / arXiv only",
        "audience": "Domain experts only"
    },
    "ai_ml": {
        "title": "Scaling Laws for Large Language Model Training on Distributed Systems",
        "abstract": """We investigate scaling laws for training large language models across distributed
        GPU clusters. Our study examines how model performance scales with compute, data, and parameter
        count when using tensor parallelism and pipeline parallelism. We derive new scaling equations
        that account for communication overhead and propose optimizations that reduce training time by
        30% for 100B+ parameter models. Our findings enable more efficient allocation of resources for
        frontier AI model development.""",
        "dissemination": "Open-source code + weights",
        "audience": "Broad developer community"
    },
    "cybersecurity": {
        "title": "Automated Vulnerability Discovery in IoT Firmware Using Symbolic Execution",
        "abstract": """Internet of Things devices often contain security vulnerabilities due to resource
        constraints and limited security testing. We present an automated framework for discovering
        vulnerabilities in IoT firmware using symbolic execution and taint analysis. Our tool identified
        47 previously unknown vulnerabilities in popular smart home devices, including buffer overflows
        and authentication bypasses. We responsibly disclosed all findings to affected vendors.""",
        "dissemination": "Conference / journal",
        "audience": "Domain experts only"
    },
    "chemistry": {
        "title": "Machine Learning-Guided Synthesis of Novel Energetic Materials",
        "abstract": """We present a machine learning framework for predicting properties of energetic
        materials and guiding synthesis of novel compounds. Our model combines graph neural networks
        with quantum chemistry calculations to predict detonation velocity, sensitivity, and stability.
        Using active learning, we synthesized three new compounds with improved performance-to-safety
        ratios compared to existing materials. This approach accelerates discovery while maintaining
        safety considerations.""",
        "dissemination": "Internal only",
        "audience": "Domain experts only"
    },
    "nuclear": {
        "title": "Advanced Fuel Cycle Modeling for Next-Generation Nuclear Reactors",
        "abstract": """This paper presents computational models for fuel cycle optimization in Generation IV
        nuclear reactors. We develop Monte Carlo simulations for neutronics analysis and couple them with
        thermal-hydraulic codes to predict reactor behavior under various operating conditions. Our models
        enable prediction of fuel burnup, actinide production, and proliferation-relevant isotope ratios.
        Results show potential for improved fuel utilization and reduced waste generation.""",
        "dissemination": "Internal only",
        "audience": "Domain experts only"
    }
}


def test_category(category: str, paper: dict) -> dict:
    """Test a single category with a sample paper"""
    payload = {
        "title": paper["title"],
        "abstract": paper["abstract"],
        "snippet": None,
        "source_url": None,
        "dissemination": paper["dissemination"],
        "audience": paper["audience"],
        "category": category
    }

    response = requests.post(f"{BASE_URL}/assess", json=payload)
    return response.json()


def validate_response(result: dict) -> tuple[bool, str]:
    """Validate that response has correct structure"""
    # Check tier
    if result.get("tier") not in ["Low", "Medium", "High", "Critical"]:
        return False, f"Invalid tier: {result.get('tier')}"

    # Check scores structure (new format with scores.scores)
    scores = result.get("scores", {})
    if "scores" in scores:
        scores = scores["scores"]

    # Check all 12 axes are present
    for axis in EXPECTED_AXES:
        if axis not in scores:
            return False, f"Missing axis: {axis}"
        if "score" not in scores[axis]:
            return False, f"Missing score for {axis}"
        if "rationale" not in scores[axis]:
            return False, f"Missing rationale for {axis}"

    # Check for parsing errors
    for axis, data in scores.items():
        if "Error parsing" in data.get("rationale", ""):
            return False, f"Parsing error in {axis}: {data['rationale']}"

    return True, "OK"


def run_all_tests():
    """Run tests for all categories and print results"""
    print("=" * 70)
    print("DUAL-USE RISK ASSESSMENT - UNIVERSAL FRAMEWORK TESTS (12 Axes)")
    print("=" * 70)

    results = {}

    for category, paper in TEST_PAPERS.items():
        print(f"\n{'='*70}")
        print(f"Testing Category: {category.upper()}")
        print(f"Paper: {paper['title'][:50]}...")
        print("-" * 70)

        try:
            result = test_category(category, paper)
            results[category] = result

            # Validate response
            valid, msg = validate_response(result)

            # Print tier
            print(f"Tier: {result['tier']}")

            # Get scores (handle both formats)
            scores = result.get("scores", {})
            if "scores" in scores:
                scores = scores["scores"]

            # Print scores grouped by section
            print("\nScores by Section:")
            current_section = None
            section_names = {
                'A': 'Capability', 'B': 'Accessibility', 'C': 'Safeguards',
                'D': 'Impact', 'E': 'Uncertainty', 'F': 'Regulatory'
            }

            for axis in sorted(scores.keys()):
                section = axis[0]
                if section != current_section:
                    print(f"\n  [{section}] {section_names.get(section, section)}:")
                    current_section = section

                score_data = scores[axis]
                score = score_data.get('score', 0)
                rationale = score_data.get('rationale', '')[:80]
                reverse = " (R)" if score_data.get('reverse_scored') else ""
                print(f"    {axis}: {score}/3{reverse} - {rationale}...")

            if valid:
                print(f"\n[OK] Assessment completed successfully")
            else:
                print(f"\n[WARN] {msg}")

        except Exception as e:
            print(f"[ERROR] Failed to test {category}: {e}")
            results[category] = {"error": str(e)}

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    success_count = 0
    for category, result in results.items():
        if "error" in result:
            status = "FAILED"
        else:
            valid, _ = validate_response(result)
            status = "OK" if valid else "PARSE_ERROR"
            if valid:
                success_count += 1

        tier = result.get('tier', 'N/A')
        print(f"  {category:15} : {status:12} | Tier: {tier}")

    print(f"\nTotal: {success_count}/{len(TEST_PAPERS)} categories passed")
    print(f"Framework: 12 Universal Axes (A1-F2)")
    return results


# Pytest integration
def test_biomedical():
    result = test_category("biomedical", TEST_PAPERS["biomedical"])
    valid, msg = validate_response(result)
    assert valid, msg


def test_semiconductor():
    result = test_category("semiconductor", TEST_PAPERS["semiconductor"])
    valid, msg = validate_response(result)
    assert valid, msg


def test_ai_ml():
    result = test_category("ai_ml", TEST_PAPERS["ai_ml"])
    valid, msg = validate_response(result)
    assert valid, msg


def test_cybersecurity():
    result = test_category("cybersecurity", TEST_PAPERS["cybersecurity"])
    valid, msg = validate_response(result)
    assert valid, msg


def test_chemistry():
    result = test_category("chemistry", TEST_PAPERS["chemistry"])
    valid, msg = validate_response(result)
    assert valid, msg


def test_nuclear():
    result = test_category("nuclear", TEST_PAPERS["nuclear"])
    valid, msg = validate_response(result)
    assert valid, msg


if __name__ == "__main__":
    run_all_tests()
