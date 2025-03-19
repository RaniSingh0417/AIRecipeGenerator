import json
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from fuzzywuzzy import process

class ActionProvideRecipe(Action):
    def name(self):
        return "action_provide_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Load recipes.json
        recipes_path = os.path.join(os.path.dirname(__file__), "recipes.json")
        try:
            with open(recipes_path, "r", encoding="utf-8") as file:
                recipes = json.load(file)
        except FileNotFoundError:
            dispatcher.utter_message(text="Sorry, I couldn't find the recipe database.")
            return []

        # Extract entities
        dish = next(tracker.get_latest_entity_values("dish"), None)
        ingredients = list(tracker.get_latest_entity_values("ingredient"))

        # Normalize dish name (split words if merged)
        if dish:
            dish = " ".join(dish.split())  # Normalize spacing

            # Get all recipe titles
            recipe_titles = [recipe["title"] for recipe in recipes]

            # Use fuzzy matching for best match
            best_match, score = process.extractOne(dish, recipe_titles)

            if score > 60:  # Lowered threshold
                matching_recipe = next(recipe for recipe in recipes if recipe["title"] == best_match)
                response = f"Here's how to make {best_match}:\nSteps:\n" + "\n".join(f"- {step}" for step in matching_recipe["steps"])
            else:
                response = f"Sorry, I couldn't find a recipe for {dish}."

        elif ingredients:
            # Find recipes that match ingredients
            matching_recipe = next((recipe for recipe in recipes if set(ingredients).issubset(set(recipe["ingredients"]))), None)
            if matching_recipe:
                response = f"Based on {', '.join(ingredients)}, try making {matching_recipe['title']}.\nSteps:\n" + "\n".join(f"- {step}" for step in matching_recipe["steps"])
            else:
                response = f"Sorry, I couldn't find a perfect match for {', '.join(ingredients)}, but you can try experimenting!"

        else:
            response = "Tell me the dish name or ingredients, and I'll suggest a recipe!"

        dispatcher.utter_message(text=response)
        return []







