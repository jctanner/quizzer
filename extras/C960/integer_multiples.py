#!/usr/bin/env python3


def main():
    numbers = list(range(10, 100))
    print('total numbers: %s' % len(numbers))

    for divisor in range(2,10):

        multiples = [x for x in numbers if x % divisor == 0]
        print('-' * 50)
        print('multiples of %s: %s ' % (divisor, len(multiples)))
        print('multiples of %s probability: %s%% ' % (divisor, (len(multiples) / len(numbers) * 100)))


if __name__ == "__main__":
    main()
