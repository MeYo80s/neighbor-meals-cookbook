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
    pkg_g: float | None = None


FOODS: tuple[FoodItem, ...] = (
    FoodItem(("cooked chicken", "shredded chicken", "chicken breast", "chicken"), 165, 31.0, 3.6, 0.0, cup_g=140),
    FoodItem(("ground turkey", "turkey"), 170, 22.0, 9.0, 0.0),
    FoodItem(("ground beef", "beef"), 254, 26.0, 17.0, 0.0),
    FoodItem(("pulled pork", "pork"), 242, 27.0, 14.0, 0.0),
    FoodItem(("egg", "eggs"), 143, 13.0, 10.0, 1.1, unit_g=50),
    FoodItem(("egg noodles",), 384, 15.0, 4.4, 71.0),
    FoodItem(("ziti pasta", "penne", "elbow macaroni", "pasta", "ziti"), 371, 13.0, 1.5, 75.0),
    FoodItem(("cooked rice", "rice"), 130, 2.7, 0.3, 28.0, cup_g=158),
    FoodItem(("potato", "potatoes"), 77, 2.0, 0.1, 17.0, unit_g=173),
    FoodItem(("carrot", "carrots"), 41, 0.9, 0.2, 10.0, unit_g=61),
    FoodItem(("celery",), 16, 0.7, 0.2, 3.0, unit_g=40),
    FoodItem(("onion",), 40, 1.1, 0.1, 9.3, unit_g=150),
    FoodItem(("garlic powder",), 331, 17.0, 0.7, 73.0, tsp_g=3.1),
    FoodItem(("garlic",), 149, 6.4, 0.5, 33.0, unit_g=3),
    FoodItem(("bell pepper",), 31, 1.0, 0.3, 6.0, unit_g=119),
    FoodItem(("broccoli",), 35, 2.4, 0.4, 7.2, cup_g=91),
    FoodItem(("cauliflower",), 25, 1.9, 0.3, 5.0, cup_g=107),
    FoodItem(("spinach",), 23, 2.9, 0.4, 3.6, cup_g=30),
    FoodItem(("mixed vegetables",), 65, 3.0, 0.3, 13.0, cup_g=160),
    FoodItem(("corn",), 96, 3.4, 1.5, 21.0, cup_g=145),
    FoodItem(("peas",), 84, 5.4, 0.4, 15.0, cup_g=145),
    FoodItem(("black beans",), 132, 8.9, 0.5, 23.7, can_g=250, cup_g=172),
    FoodItem(("kidney beans",), 127, 8.7, 0.5, 22.8, can_g=250, cup_g=177),
    FoodItem(("pinto beans",), 143, 9.0, 0.7, 26.0, can_g=250, cup_g=171),
    FoodItem(("diced tomatoes", "tomatoes"), 18, 0.9, 0.2, 3.9, can_g=400, cup_g=245),
    FoodItem(("tomato paste",), 82, 4.3, 0.5, 19.0, tbsp_g=16),
    FoodItem(("marinara", "pasta sauce", "tomato sauce"), 56, 1.8, 1.7, 8.4, cup_g=250, can_g=680),
    FoodItem(("chicken broth", "chicken stock"), 15, 1.0, 0.5, 1.0, cup_g=240),
    FoodItem(("beef broth", "beef stock"), 10, 1.0, 0.4, 0.5, cup_g=240),
    FoodItem(("cream of chicken soup",), 75, 2.0, 4.0, 8.0, cup_g=250, can_g=300),
    FoodItem(("cream of mushroom soup",), 78, 1.6, 5.0, 7.0, cup_g=250, can_g=300),
    FoodItem(("sour cream",), 193, 2.4, 19.0, 4.6, cup_g=230, tbsp_g=14),
    FoodItem(("ricotta",), 174, 11.0, 13.0, 3.0, cup_g=246),
    FoodItem(("cream cheese",), 342, 6.2, 34.0, 4.1, tbsp_g=14, pkg_g=226),
    FoodItem(("cottage cheese",), 98, 11.0, 4.3, 3.4, cup_g=226),
    FoodItem(("cheddar cheese", "cheddar"), 403, 25.0, 33.0, 1.3, cup_g=113),
    FoodItem(("mozzarella",), 280, 28.0, 17.0, 3.1, cup_g=112),
    FoodItem(("parmesan",), 431, 38.0, 29.0, 4.1, cup_g=100),
    FoodItem(("monterey jack",), 373, 25.0, 30.0, 1.3, cup_g=113),
    FoodItem(("milk",), 61, 3.2, 3.3, 4.8, cup_g=245),
    FoodItem(("heavy cream",), 340, 2.1, 36.0, 2.8, cup_g=238, tbsp_g=15),
    FoodItem(("butter",), 717, 0.9, 81.0, 0.1, tbsp_g=14, unit_g=113),
    FoodItem(("olive oil",), 884, 0.0, 100.0, 0.0, tbsp_g=13.5, tsp_g=4.5),
    FoodItem(("vegetable oil", "canola oil", "oil"), 884, 0.0, 100.0, 0.0, tbsp_g=13.5, tsp_g=4.5),
    FoodItem(("flour",), 364, 10.0, 1.0, 76.0, cup_g=120, tbsp_g=7.5),
    FoodItem(("sugar",), 387, 0.0, 0.0, 100.0, cup_g=200, tbsp_g=12.5),
    FoodItem(("brown sugar",), 380, 0.1, 0.0, 98.0, cup_g=220, tbsp_g=13.8),
    FoodItem(("honey",), 304, 0.3, 0.0, 82.0, tbsp_g=21),
    FoodItem(("maple syrup",), 260, 0.0, 0.1, 67.0, tbsp_g=20),
    FoodItem(("oats", "oatmeal"), 389, 17.0, 6.9, 66.0, cup_g=81),
    FoodItem(("breadcrumbs",), 395, 13.0, 5.0, 72.0, cup_g=108),
    FoodItem(("tortilla", "tortillas"), 310, 8.0, 8.0, 51.0, unit_g=50),
    FoodItem(("italian seasoning",), 265, 11.0, 7.0, 51.0, tsp_g=1.0),
    FoodItem(("chili powder",), 282, 13.0, 14.0, 50.0, tbsp_g=8),
    FoodItem(("cumin",), 375, 18.0, 22.0, 44.0, tsp_g=2.1),
    FoodItem(("paprika",), 282, 14.0, 13.0, 54.0, tsp_g=2.3),
    FoodItem(("black pepper", "pepper"), 251, 10.0, 3.3, 64.0, tsp_g=2.3),
    FoodItem(("salt",), 0.0, 0.0, 0.0, 0.0),
)

FRACTIONS = {
    "1/8": 0.125,
    "1/4": 0.25,
    "1/3": 0.333,
    "1/2": 0.5,
    "2/3": 0.667,
    "3/4": 0.75,
    "⅛": 0.125,
    "¼": 0.25,
    "⅓": 0.333,
    "½": 0.5,
    "⅔": 0.667,
    "¾": 0.75,
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
    "package": "pkg",
    "packages": "pkg",
    "pkg": "pkg",
    "stick": "unit",
    "sticks": "unit",
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


def ingredient_to_grams(qty: float, unit: str, food: FoodItem) -> float:
    if unit == "lb":
        return qty * 453.592
    if unit == "oz":
        return qty * 28.3495
    if unit == "can":
        return qty * (food.can_g if food.can_g is not None else 400)
    if unit == "jar":
        return qty * (food.can_g if food.can_g is not None else 650)
    if unit == "pkg":
        return qty * (food.pkg_g if food.pkg_g is not None else 454)
    if unit == "cup":
        return qty * (food.cup_g if food.cup_g is not None else 240)
    if unit == "tbsp":
        if food.tbsp_g is not None:
            return qty * food.tbsp_g
        return qty * ((food.cup_g / 16.0) if food.cup_g is not None else 15)
    if unit == "tsp":
        if food.tsp_g is not None:
            return qty * food.tsp_g
        return qty * ((food.cup_g / 48.0) if food.cup_g is not None else 5)
    if unit == "unit":
        return qty * (food.unit_g if food.unit_g is not None else 50)
    return qty * 50


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
