#!/usr/bin/python3
import re


def parse_input():
    """
    Parse input.txt to mapping of products to components
    """
    reaction_regex = re.compile(r'(?P<ingredients>((\d+ \w+,?)[, ]*)+) => (?P<product>\d+ \w+)')
    component_regex = re.compile(r'(?P<quantity>\d+) (?P<chemical>\w+)')

    product_to_components = {}

    with open('input.txt', 'r') as txt:
        for reaction in txt:
            reaction_parts = reaction_regex.match(reaction).groupdict()

            product = component_regex.match(reaction_parts['product']).groupdict()
            ingredients = component_regex.finditer(reaction_parts['ingredients'])

            product_to_components[product['chemical']] = (
                int(product['quantity']),
                [(int(ingredient['quantity']), ingredient['chemical']) for ingredient in ingredients]
            )

    return product_to_components


def get_ore_count(product_to_components, requirements):
    reacting = [chemical for chemical in requirements if requirements[chemical] > 0 and chemical != 'ORE']

    while reacting:
        for chemical in reacting:
            amount, ingredients = product_to_components[chemical]
            multiplier = (requirements[chemical] + amount - 1) // amount

            for (ingredient_amount, ingredient_ingredients) in ingredients:
                requirements[ingredient_ingredients] = requirements.get(ingredient_ingredients, 0) + multiplier * ingredient_amount

            requirements[chemical] -= multiplier * amount

        reacting = [chemical for chemical in requirements if requirements[chemical] > 0 and chemical != 'ORE']

    return requirements["ORE"]


def main():
    product_to_components = parse_input()
    requirements = {'FUEL': 1}

    needed_ore = get_ore_count(product_to_components, requirements)

    print(f'Part One: {needed_ore}')

    high = 5000000
    low = 1
    test_value = None
    target = 1000000000000

    while high >= low:
        test_value = (high + low) // 2
        test_ore_count = get_ore_count(product_to_components, {'FUEL': test_value})
        if test_ore_count < target:
            low = test_value + 1
        elif test_ore_count > target:
            high = test_value - 1
        else:
            break

    print(f'Part Two: {test_value}')


if __name__ == '__main__':
    main()
