#!/usr/bin/python3


def parse_input(x, y):
    """
    Parse input.txt to layers
    """

    layers = []

    with open('input.txt', 'r') as txt:
        layer = []
        for index, data in enumerate(list(txt.read().strip())):
            if index % (x * y) == 0:
                layer = []
                layers.append(layer)
            layer.append(data)

    return layers


def main():
    layers = parse_input(25, 6)

    min_0_layer = min(layers, key=lambda x: x.count("0"))

    print(f'Part One: {min_0_layer.count("1") * min_0_layer.count("2")}')


if __name__ == '__main__':
    main()
