#!/usr/bin/env python


class Person:
    def __init__(self):
        self.domino = False
        self.falcon = False
        self.giant = False

        self.IT = False

def by_projects(projects, people):
    total = people[:]
    for project in projects:
        total = [x for x in total if getattr(x, project)]
    return total

def by_single_project(project, people):
    projects = ['domino', 'falcon', 'giant']
    projects.remove(project)
    total = people[:]
    for _project in projects:
        total = [x for x in total if not getattr(x, _project)]
    return total

def main():
    people = []

    # Add the 4 IT people ...
    for x in range(0,4):
        #print(x)
        np = Person()
        np.IT = True
        np.domino = True
        np.falcon = True
        np.giant = True
        people.append(np)
    
    for x in range(0, 4):
        np = Person()
        np.domino = True
        np.falcon = True
        people.append(np)
    
    for x in range(0, 2):
        np = Person()
        np.falcon = True
        np.giant = True
        people.append(np)
    
    for x in range(0, 3):
        np = Person()
        np.giant = True
        np.domino = True
        people.append(np)

    while len(by_projects(['domino'], people)) < 19:
        np = Person()
        np.domino = True
        people.append(np)
    
    while len(by_projects(['falcon'], people)) < 16:
        np = Person()
        np.falcon = True
        people.append(np)
    
    while len(by_projects(['giant'], people)) < 15:
        np = Person()
        np.giant = True
        people.append(np)

    print('domino*: %s' % len([x for x in people if x.domino]))
    print('falcon*: %s' % len([x for x in people if x.falcon]))
    print('giant*: %s' % len([x for x in people if x.giant]))

    print('domino: %s' % len(by_single_project('domino', people)))
    print('falcon: %s' % len(by_single_project('falcon', people)))
    print('giant: %s' % len(by_single_project('giant', people)))

    print('d+f: %s' % len(by_projects(['domino', 'falcon'], people)))
    print('f+g: %s' % len(by_projects(['falcon', 'giant'], people)))
    print('g+d: %s' % len(by_projects(['giant', 'domino'], people)))

    print('total: %s' % len(people))


if __name__ == "__main__":
    main()