#!/usr/bin/python3
import math

def parse_input():
    """
    Parse input.txt to list of masses
    """

    masses = []

    with open('input.txt', 'r') as input:
        for mass in input:
            masses.append(mass.strip())

    return masses


def calculate_fuel(masses):
    """
    Calculate fuel requirements for each module's mass
    """
    total_fuel = []

    for mass in masses:
        fuel = math.floor(int(mass) / 3) - 2
        total_fuel.append(fuel if fuel >= 0 else 0)

    return total_fuel

def main():
    masses = parse_input()
    module_fuel = calculate_fuel(masses)

    total_fuel = sum(module_fuel)

    print(f'Total Fuel for modules: {total_fuel}')

    fuels_fuel = calculate_fuel(module_fuel)
    while sum(fuels_fuel):
        total_fuel += sum(fuels_fuel)
        fuels_fuel = calculate_fuel(fuels_fuel)

    print(f'Total Fuel for modules & fuel: {total_fuel}')

if __name__ == '__main__':
    main()

