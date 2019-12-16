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
    """
    base_pattern = [0, 1, 0, -1]
    """
    signal_length = len(input_signal)
    output_signal = []

    for output_index in range(0, signal_length):
        calculated_value = 0
        for calc_index in range(output_index, signal_length):
            pattern_index = ((calc_index + 1) // (output_index + 1)) % 4
            if pattern_index == 1:
                calculated_value += input_signal[calc_index]
            elif pattern_index == 3:
                calculated_value -= input_signal[calc_index]
        output_signal.append(abs(calculated_value) % 10)

    return output_signal


def run_quick_phase(input_signal):
    signal_length = len(input_signal)
    output_signal = []
    prior_calculated_value = None

    for output_index in range(0, signal_length):
        if not prior_calculated_value:
            calculated_value = sum(input_signal)
        else:
            calculated_value = prior_calculated_value - input_signal[output_index - 1]
        prior_calculated_value = calculated_value
        output_signal.append(abs(calculated_value) % 10)

    return output_signal


def part_one(signal):
    for phase in range(1, 101):
        signal = run_phase(signal)

    return signal


def part_two(signal):
    for phase in range(1, 101):
        signal = run_quick_phase(signal)

    return signal


def main():
    input_signal = parse_input()
    message = part_one(input_signal)

    print(f'Part One: {"".join(map(str, message))[:8]}')

    message_offset = int("".join(map(str, input_signal))[:7])
    print(f'Offset  : {message_offset}')

    input_signal *= 10000

    assert message_offset > len(input_signal) // 2

    message = part_two(input_signal[message_offset:])
    print(f'Part Two: {"".join(map(str, message))[:8]}')


if __name__ == '__main__':
    main()
