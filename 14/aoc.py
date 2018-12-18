#!/usr/bin/python


def combine_recipes(scores, elf1, elf2, recipe_count):
    while len(scores) < recipe_count + 10:
        new_score = scores[elf1] + scores[elf2]
        scores.extend(map(int, list(str(new_score))))
        elf1 = (elf1 + 1 + scores[elf1]) % len(scores)
        elf2 = (elf2 + 1 + scores[elf2]) % len(scores)
    return ''.join(map(str, scores[recipe_count:recipe_count+10]))


def main():
    scores = [3, 7]
    elf1 = 0
    elf2 = 1

    part_one = combine_recipes(scores, elf1, elf2, 77201)

    print(f'Part One: {part_one}')


if __name__ == '__main__':
    main()
