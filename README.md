# Safecrate - Content Safety Validator

A comprehensive content safety analysis tool for Indian content creators, with special focus on women's safety.

## Features

- **Multi-Category Analysis**: Violence, sexual content, harassment, privacy, and more
- **Women's Safety Focus**: Special analyzer for women's safety in Indian context
- **Legal Compliance**: IT Act, IPC, POSH Act checks
- **Quick Quiz**: 10-question safety assessment
- **Compliance Reports**: Exportable reports for creators

## Quick Start

```bash
cd safecrate
pip install -e .
python demo.py
```

## Usage

```python
from safecrate import ContentAnalyzer, SensitivityScorer

# Analyze content
analyzer = ContentAnalyzer()
results = analyzer.analyze(metadata=video_metadata)

# Calculate overall risk
scorer = SensitivityScorer()
score = scorer.calculate_score(results)
```

## For Content Creators

Safecrate helps you:
1. Check if your content is safe to post
2. Ensure compliance with Indian laws
3. Protect women's safety and dignity
4. Get actionable recommendations

## Legal Disclaimer

This tool provides guidance only and does not constitute legal advice. Always consult a qualified lawyer for legal matters.
