#!/usr/bin/python3


def parse_input():
    """
    Parse input.txt to input signal
    """

    input_signal = []

    with open('input.txt', 'r') as txt:
        for digit in txt.read().strip():
            input_signal.append(int(digit))

    return input_signal


def run_phase(input_signal):
    base_pattern = [0, 1, 0, -1]
    signal_length = len(input_signal)
    output_signal = []

    for output_index, digit in enumerate(input_signal):
        calculated_value = 0
        for calc_index in range(output_index, signal_length):
            pattern_index = ((calc_index + 1) // (output_index + 1)) % 4
            calculated_value += input_signal[calc_index] * base_pattern[pattern_index]
        output_signal.append(abs(calculated_value) % 10)

    return output_signal


def part_one(signal):
    for phase in range(1, 101):
        signal = run_phase(signal)

    print("".join(map(str, signal))[:8])


def main():
    input_signal = parse_input()
    part_one(input_signal)


if __name__ == '__main__':
    main()
