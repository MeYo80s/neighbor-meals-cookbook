# Neighbor Meals Cookbook

Shareable ward cookbook for comforting meals delivered to neighbors and friends during illness, loss, recovery, or welcoming a new baby.

## Repository
- Public link: [neighbor-meals-cookbook](https://github.com/MeYo80s/neighbor-meals-cookbook)

## Live Cookbook Website (GitHub Pages)
- Expected URL: [https://meyo80s.github.io/neighbor-meals-cookbook/](https://meyo80s.github.io/neighbor-meals-cookbook/)
- One-time setup in GitHub:
  1. Go to `Settings > Pages`.
  2. Under `Build and deployment`, set `Source` to `GitHub Actions`.
  3. Push to `main` (or run the `Deploy Cookbook Site` workflow manually).

## What This Includes
- Home-cooked freezer meal recipes
- Ready-to-purchase drop-off options
- Simple homemade meal ideas that travel well
- Auto-estimated calories and macros per serving

## For Contributors
1. Copy `templates/recipe-template.md` into `recipes/<category>/your-recipe-name.md`.
2. Fill in recipe details and ingredient list.
3. Add your recipe link in `RECIPE_INDEX.md` under the right category.
4. Run:
   - `python3 scripts/auto_nutrition.py`
   - `python3 scripts/generate_recipe_book.py`
5. Open a pull request.

## Maintainer Commands
- Recalculate recipe macros: `python3 scripts/auto_nutrition.py`
- Rebuild cookbook markdown + website: `python3 scripts/generate_recipe_book.py`

## Notes
- Macro values are estimates based on standard ingredient data.
- Brand differences and custom substitutions can change nutrition totals.
