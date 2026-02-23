# Contributing Recipes

Thank you for contributing to the Neighbor Meals Cookbook.

## Recipe Standards
- Keep recipes simple and family-friendly.
- Include clear serving size and transport tips.
- Use bullet points for ingredients and numbered steps for instructions.

## Steps to Submit
1. Create a recipe file from `templates/recipe-template.md`.
2. Save in a category folder under `recipes/`.
3. Add the recipe to `RECIPE_INDEX.md`.
4. Run:
   - `python3 scripts/auto_nutrition.py`
   - `python3 scripts/generate_recipe_book.py`
5. Commit all changed files and open a pull request.

## Nutrition Estimates
- `scripts/auto_nutrition.py` auto-adds estimated calories/macros per serving.
- If a recipe has unusual ingredients, check and adjust manually if needed.
