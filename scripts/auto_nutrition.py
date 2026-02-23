#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE_GLOB = "recipes/**/*.md"


@dataclass(frozen=True)
class FoodItem:
    keywords: tuple[str, ...]
    cal_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    cup_g: float | None = None
    tbsp_g: float | None = None
    tsp_g: float | None = None
    unit_g: float | None = None
    can_g: float | None = None


FOODS: tuple[FoodItem, ...] = (
    FoodItem(("cooked chicken", "shredded chicken", "chicken"), 165, 31, 3.6, 0, cup_g=140),
    FoodItem(("cooked rice", "rice"), 130, 2.7, 0.3, 28, cup_g=158),
    FoodItem(("cream of chicken soup",), 75, 2.0, 4.0, 8.0, cup_g=250, can_g=300),
    FoodItem(("sour cream",), 193, 2.4, 19.0, 4.6, cup_g=230, tbsp_g=14),
    FoodItem(("cheddar cheese", "cheddar"), 403, 25, 33, 1.3, cup_g=113),
    FoodItem(("mixed vegetables",), 65, 3.0, 0.3, 13.0, cup_g=160),
    FoodItem(("garlic powder",), 331, 17.0, 0.7, 73.0, tsp_g=3.1),
    FoodItem(("ground turkey", "turkey"), 170, 22.0, 9.0, 0.0),
    FoodItem(("onion",), 40, 1.1, 0.1, 9.3, unit_g=150),
    FoodItem(("garlic",), 149, 6.4, 0.5, 33.0, unit_g=3),
    FoodItem(("diced tomatoes", "tomatoes"), 18, 0.9, 0.2, 3.9, can_g=400, cup_g=245),
    FoodItem(("kidney beans",), 127, 8.7, 0.5, 22.8, can_g=250, cup_g=177),
    FoodItem(("black beans",), 132, 8.9, 0.5, 23.7, can_g=250, cup_g=172),
    FoodItem(("chili powder",), 282, 13.0, 14.0, 50.0, tbsp_g=8),
    FoodItem(("cumin",), 375, 18.0, 22.0, 44.0, tsp_g=2.1),
    FoodItem(("salt",), 0, 0, 0, 0),
    FoodItem(("ziti pasta", "pasta", "ziti"), 371, 13.0, 1.5, 75.0),
    FoodItem(("marinara", "pasta sauce"), 56, 1.8, 1.7, 8.4, cup_g=250, can_g=680),
    FoodItem(("ricotta",), 174, 11.0, 13.0, 3.0, cup_g=246),
    FoodItem(("mozzarella",), 280, 28.0, 17.0, 3.1, cup_g=112),
    FoodItem(("parmesan",), 431, 38.0, 29.0, 4.1, cup_g=100),
    FoodItem(("egg", "eggs"), 143, 13.0, 10.0, 1.1, unit_g=50),
    FoodItem(("italian seasoning",), 265, 11.0, 7.0, 51.0, tsp_g=1.0),
)

FRACTIONS = {
    "1/8": 0.125,
    "1/4": 0.25,
    "1/3": 0.333,
    "1/2": 0.5,
    "2/3": 0.667,
    "3/4": 0.75,
}

UNIT_ALIASES = {
    "cup": "cup",
    "cups": "cup",
    "tbsp": "tbsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "can": "can",
    "cans": "can",
    "jar": "jar",
    "jars": "jar",
    "clove": "unit",
    "cloves": "unit",
    "egg": "unit",
    "eggs": "unit",
}


def parse_servings(text: str) -> float:
    m = re.search(r"\*\*Serves/Yield:\*\*\s*([^\n]+)", text, flags=re.IGNORECASE)
    if not m:
        return 1.0
    serving_text = m.group(1).strip()
    nums = re.findall(r"\d+(?:\.\d+)?", serving_text)
    if not nums:
        return 1.0
    values = [float(n) for n in nums]
    if len(values) == 1:
        return max(values[0], 1.0)
    return max(sum(values) / len(values), 1.0)


def parse_qty(token: str) -> float | None:
    token = token.strip().lower()
    if token in FRACTIONS:
        return FRACTIONS[token]
    if re.fullmatch(r"\d+", token):
        return float(token)
    if re.fullmatch(r"\d+\.\d+", token):
        return float(token)
    if re.fullmatch(r"\d+/\d+", token):
        n, d = token.split("/")
        if float(d) == 0:
            return None
        return float(n) / float(d)
    return None


def parse_ingredient_line(line: str) -> tuple[float, str, str] | None:
    line = line.strip()
    if not line.startswith("- "):
        return None
    body = line[2:].strip()
    if not body or "to taste" in body.lower():
        return None

    tokens = re.split(r"\s+", body)
    if not tokens:
        return None

    qty = parse_qty(tokens[0])
    idx = 1
    if qty is None:
        return None

    if idx < len(tokens):
        next_qty = parse_qty(tokens[idx])
        if next_qty is not None:
            qty += next_qty
            idx += 1

    unit = "unit"
    if idx < len(tokens):
        candidate = re.sub(r"[^a-zA-Z]", "", tokens[idx]).lower()
        if candidate in UNIT_ALIASES:
            unit = UNIT_ALIASES[candidate]
            idx += 1

    ingredient_text = " ".join(tokens[idx:]).lower()
    return qty, unit, ingredient_text


def ingredient_to_grams(qty: float, unit: str, food: FoodItem) -> float | None:
    if unit == "lb":
        return qty * 453.592
    if unit == "oz":
        return qty * 28.3495
    if unit == "can":
        if food.can_g is not None:
            return qty * food.can_g
        return qty * 400
    if unit == "jar":
        if food.can_g is not None:
            return qty * food.can_g
        return qty * 650
    if unit == "cup":
        if food.cup_g is not None:
            return qty * food.cup_g
        return qty * 240
    if unit == "tbsp":
        if food.tbsp_g is not None:
            return qty * food.tbsp_g
        if food.cup_g is not None:
            return qty * (food.cup_g / 16.0)
        return qty * 15
    if unit == "tsp":
        if food.tsp_g is not None:
            return qty * food.tsp_g
        if food.cup_g is not None:
            return qty * (food.cup_g / 48.0)
        return qty * 5
    if unit == "unit":
        if food.unit_g is not None:
            return qty * food.unit_g
        return qty * 50
    return None


def find_food(ingredient_text: str) -> FoodItem | None:
    for food in sorted(FOODS, key=lambda f: max(len(k) for k in f.keywords), reverse=True):
        for keyword in food.keywords:
            if keyword in ingredient_text:
                return food
    return None


def extract_ingredients_block(text: str) -> list[str]:
    m = re.search(r"### Ingredients\n(.*?)(\n### |\Z)", text, flags=re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    return [line.rstrip() for line in block.splitlines() if line.strip().startswith("- ")]


def format_macro_line(cal: float, protein: float, fat: float, carbs: float, servings: float, coverage: float) -> str:
    coverage_note = ""
    if coverage < 0.6:
        coverage_note = " (low ingredient match - review suggested)"
    return (
        "**Estimated macros (auto):** "
        f"~{round(cal)} cal | {round(protein)}g protein | {round(fat)}g fat | {round(carbs)}g carbs "
        f"(per serving, serves {round(servings)}){coverage_note}"
    )


def update_macro_line(text: str, new_line: str) -> str:
    if re.search(r"^\*\*Estimated macros \(auto\):\*\*.*$", text, flags=re.MULTILINE):
        return re.sub(r"^\*\*Estimated macros \(auto\):\*\*.*$", new_line, text, flags=re.MULTILINE)
    if re.search(r"^\*\*Cook time:\*\*.*$", text, flags=re.MULTILINE):
        return re.sub(r"(^\*\*Cook time:\*\*.*$)", r"\1\n" + new_line, text, count=1, flags=re.MULTILINE)
    lines = text.splitlines()
    lines.insert(1, new_line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def process_recipe(path: Path) -> tuple[bool, str]:
    original = path.read_text(encoding="utf-8")
    servings = parse_servings(original)
    ingredient_lines = extract_ingredients_block(original)

    total_cal = total_p = total_f = total_c = 0.0
    matched = 0

    for line in ingredient_lines:
        parsed = parse_ingredient_line(line)
        if parsed is None:
            continue
        qty, unit, ingredient_text = parsed
        food = find_food(ingredient_text)
        if food is None:
            continue
        grams = ingredient_to_grams(qty, unit, food)
        if grams is None:
            continue

        factor = grams / 100.0
        total_cal += food.cal_per_100g * factor
        total_p += food.protein_per_100g * factor
        total_f += food.fat_per_100g * factor
        total_c += food.carbs_per_100g * factor
        matched += 1

    if servings <= 0:
        servings = 1

    coverage = (matched / len(ingredient_lines)) if ingredient_lines else 0.0
    macro_line = format_macro_line(
        cal=total_cal / servings,
        protein=total_p / servings,
        fat=total_f / servings,
        carbs=total_c / servings,
        servings=servings,
        coverage=coverage,
    )

    updated = update_macro_line(original, macro_line)
    changed = updated != original
    if changed:
        path.write_text(updated, encoding="utf-8")
    return changed, f"{path.as_posix()}: {macro_line}"


def main() -> None:
    recipes = sorted(ROOT.glob(RECIPE_GLOB))
    if not recipes:
        print("No recipes found.")
        return

    changed_count = 0
    for recipe in recipes:
        changed, msg = process_recipe(recipe)
        if changed:
            changed_count += 1
        print(msg)

    print(f"\nUpdated {changed_count} recipe file(s).")


if __name__ == "__main__":
    main()
