# Smart Food Forge — SIH Upgraded Prototype

A hackathon-ready prototype for **AI-based intelligent food packaging material recommendation**.

## What is upgraded
- Screenshot-inspired professional decision dashboard
- Shelf-life slider, storage condition and food commodity inputs
- Balanced / Eco-first / Budget-first / Max protection priorities
- Explainable scoring engine with protection, cost, sustainability and shelf-life dimensions
- 0–100 fit score with visual ring
- Cost, protection, footprint and suitability metrics
- "Why this material?" explanation panel
- Decision profile bars
- Ranked alternative packaging options
- Quick demo presets for a live judge walkthrough
- Copy result + print report actions
- Responsive mobile layout and print stylesheet
- `/api/health` endpoint for deployment checks
- No API key or external AI service is required for the core demo

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Suggested SIH demo
1. Select Dairy + Refrigerated + 10 days + Balanced.
2. Click Recommend packaging.
3. Explain the fit score, cost, protection, footprint and decision profile.
4. Switch to Eco-first and run again to show that the ranking changes with the user's objective.
5. Use Meat + Frozen + 30 days + Max protection to show a different scenario.

## Note
This is a decision-support prototype. Packaging recommendations should be validated with real product characteristics, regulatory requirements, packaging test data and food-safety professionals before production use.
