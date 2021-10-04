import requests
import csv


# Recipe search API https://developer.edamam.com/edamam-docs-recipe-api
# If successful the output is max 10 recipes
def recipe_search(ingredient, time, diet):
    recipe_app_id = 'REDACTED'
    recipe_app_key = 'REDACTED'
    if diet == "none":
        # this url excludes diet parameter and includes time as additional parameter
        url = 'https://api.edamam.com/search?q={}&time=1-{}&app_id={}&app_key={}'.format(ingredient, time,
                                                                                         recipe_app_id, recipe_app_key)
    else:
        # this url includes diet parameter as additional parameter
        url = 'https://api.edamam.com/search?q={}&time=1-{}&diet={}&app_id={}&app_key={}'.format(ingredient, time, diet,
                                                                                                 recipe_app_id,
                                                                                                 recipe_app_key)
    # Two dietary labels has response code 403 error, therefore checking code status
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        return data['hits']
    else:
        print('Could not find data')


# Nutritional analysis API https://developer.edamam.com/edamam-docs-nutrition-api
def nutrition_data(ingredient):
    nutrition_app_id = '4630cfa0'
    nutrition_app_key = '7aebbfe268862151ee8827fe8a3f079f'
    result = requests.get(
        'https://api.edamam.com/api/nutrition-data?ingr={}&nutrition-type=logging&app_id={}&app_key={}'.format(
            ingredient, nutrition_app_id, nutrition_app_key)
    )
    if result.status_code == 200:
        data = result.json()
        return data
    else:
        print('Could not find data')


# Save the results to a file
def recipe_to_file(recipe_list, field_names):
    with open('recipe.csv', 'w+') as csv_file:
        spreadsheet = csv.DictWriter(csv_file, fieldnames=field_names)
        spreadsheet.writeheader()
        spreadsheet.writerows(recipe_list)


# Main program
def run():
    global field_names
    print('What ingredient would you like to search today?')
    ingredient = input()
    while ingredient == "" or ingredient.isalpha() is False:
        ingredient = input("Please re-enter an ingredient: \n")
    time = input('Enter maximum total cooking and prep time in minutes: ')
    while time == "" or time.isdigit() is False:
        time = input("Please re-enter a time in minutes: \n")
    diet = input("Enter letter of the dietary requirement you're interested in: \n"
                 "a) balanced, b) high-fiber, c) high-protein, d) low-carb, e) low-fat, f) low-sodium g) none: ")
    while len(diet) != 1 or diet.lower() not in "abcdefg":
        diet = input("Please re-enter letter of the dietary requirement you're interested in: \n")
    diets = {"a": "balanced", "b": "high-fiber", "c": "high-protein", "d": "low-carb", "e": "low-fat",
             "f": "low-sodium", "g": "none"}
    diet = diets.get(diet)

    # Cross-reference the ingredient against the Edamam nutrition analysis API
    print("\nIngredient nutrition: " + str(
        nutrition_data(ingredient)['totalWeight']) + "g of " + ingredient + " has " + str(
        nutrition_data(ingredient)['calories']) + " kcal ")

    # Searching for recipes using the Edamam recipe analysis API
    print(
        "\nBased on your answers, here are a list of recipes you may want to try. Further details of these recipes can be found in a csv file sorted by Calories:")
    results = recipe_search(ingredient, time, diet)
    recipe_list = []
    if results is not None:
        for result in results:
            recipe = result['recipe']

            # Header list format created for the CSV file
            field_names = ["Recipe name", "image link", "url link", "Servings", "Total calories per recipe (kcal)",
                           "Total time (mins)"]

            # Dictionary format for each recipe
            recipe_detail = {"Recipe name": recipe['label'].title(), "image link": recipe['image'],
                             "url link": recipe['url'],
                             "Servings": (recipe['yield']),
                             "Total calories per recipe (kcal)": (round(recipe['calories'])),
                             "Total time (mins)": (round(recipe['totalTime']))}

            # Dictionary format for each recipe appended to a list format
            recipe_list.append(recipe_detail)

        # List of recipes is sorted by Calories parameter
        recipe_list = sorted(recipe_list, key=lambda k: k['Total calories per recipe (kcal)'])

        # Display the recipes for each search result, the output is the recipe name and url link
        for recipe in recipe_list:
            print(recipe['Recipe name'] + ": " + recipe['url link'])

        # Write to csv file
        recipe_to_file(recipe_list, field_names)


# Looping program
def recipe_request():
    new_recipe = input('\nWould you like to search for recipes? Enter y/n: ').lower()
    while new_recipe == 'y':
        run()
        new_recipe = input('\nWould you like to search for different recipes? Enter y/n: ').lower()
    if new_recipe == 'n':
        quit()
    else:
        recipe_request()


# Run full program
recipe_request()