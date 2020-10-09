#!/usr/bin/env python


def main():
    l0 = 0
    lN = 39

    total = 0
    last_sum = None
    for l in range(l0, lN+1):
        lsum = 1 + 5*l
        total += lsum
        if last_sum:
            delta = lsum - last_sum
        else:
            delta = 0
        last_sum = lsum
        print(f'{l} ... 1 + 5*{l} = {lsum} ... delta: {delta}')

    print(total)


if __name__ == "__main__":
    main()
