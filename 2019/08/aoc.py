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

    final_image = []

    for pixel in range(0, 25 * 6):
        for layer_index in range(0, len(layers)):
            if layers[layer_index][pixel] != '2':
                final_image.append(layers[layer_index][pixel])
                break

    for y in range(0, 6):
        for x in range(0, 25):
            print(' ' if final_image[(y*25) + x] == '0' else '█', end='')
        print()


if __name__ == '__main__':
    main()
