#!/usr/bin/python3


class Password:

    class OutOfRange(Exception):
        def __init__(self, number):
            self.number = number

        def __str__(self):
            return f'Password out of range {self.number}'

    def __init__(self, number):
        if not 130254 <= number <= 678275:
            raise Password.OutOfRange(number)
        self.digits = [int(x) for x in str(number)]

    def __str__(self):
        return "".join(map(str, self.digits))

    def __repr__(self):
        return int(self.__str__())

    @property
    def valid(self):
        contains_double = False
        never_decreases = True
        triple_digit = 0

        for index in range(0, 5):
            if self.digits[index] == self.digits[index + 1]:
                if index < 4:
                    if self.digits[index] == self.digits[index + 2]:
                        triple_digit = self.digits[index]
                    else:
                        if self.digits[index] != triple_digit:
                            contains_double = True
                else:
                    if self.digits[index] != triple_digit:
                        contains_double = True
            if self.digits[index + 1] < self.digits[index]:
                never_decreases = False

        return contains_double and never_decreases

    def increment_number(self):
        digits = self.digits.copy()
        for reverse_digit in range(5, -1, -1):
            if digits[reverse_digit] < 9:
                digits[reverse_digit] += 1
                for replace in range(reverse_digit, 6, 1):
                    digits[replace] = digits[reverse_digit]
                break
        return int("".join(map(str, digits)))

    def next_password(self):
        next_password = Password(self.increment_number())
        while not next_password.valid:
            next_password = Password(next_password.increment_number())
        return next_password


def main():
    password = Password(130254)
    valid_count = 0

    if password.valid:
        valid_count += 1

    try:
        while True:
            password = password.next_password()
            valid_count += 1
    except Password.OutOfRange as exc:
        print(exc)

    print(f'Valid passwords: {valid_count}')


if __name__ == '__main__':
    main()
