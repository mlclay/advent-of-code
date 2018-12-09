#!/usr/bin/python


class Node:

    def __init__(self, num_children, num_metadata):
        self.num_children = int(num_children)
        self.num_metadata = int(num_metadata)
        self.children = []
        self.metadata = []

    def __str__(self):
        return f'#Children: {self.num_children}  Meta: {[x for x in self.metadata]}'

    def calculate_metadata_sum(self):
        """
        Calculate sum of metadata and all children's metadata

        :return: metadata sum
        """
        return sum(self.metadata) + sum([child.calculate_metadata_sum() for child in self.children])

    @staticmethod
    def generate_from_list(tree):
        """
        From Input list, generate all Nodes from base node

        :param tree: List of input numbers
        :return: First Node with populated children Nodes and Metadata
        """
        node = Node(tree[0], tree[1])

        for number in range(1, node.num_children + 1):
            tree, child = Node.generate_from_list(tree[2:])
            node.children.append(child)

        node.metadata = [int(x) for x in tree[2: 2 + node.num_metadata]]

        tree = tree[node.num_metadata:]

        return tree, node


def parse_input():
    """
    Parse input.txt to string

    :return: list of tuples defining X,Y coordinates
    """

    with open('input.txt', 'r') as txt:
        tree = txt.read().strip().split(' ')

    return tree


def main():
    tree = parse_input()

    tree, node = Node.generate_from_list(tree)

    print(f'Part One: {node.calculate_metadata_sum()}')


if __name__ == '__main__':
    main()
