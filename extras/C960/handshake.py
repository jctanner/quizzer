#!/usr/bin/env python


def main():
    people = list(range(0,27))
    people = [chr(65+x) for x in people]

    shakes = set()
    for x in people:
        for y in people:
            if x == y:
                continue
            shakes.add(''.join(sorted([x,y])))

    print(f'{len(list(shakes))} total handshakes')


if __name__ == "__main__":
    main()
