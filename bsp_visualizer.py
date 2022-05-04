#!/usr/bin/env python3
# Eryn Wells <eryn@erynwells.me>

import argparse
import tcod

def parse_args(argv, *a, **kw):
    parser = argparse.ArgumentParser(*a, **kw)
    parser.add_argument('width', type=int)
    parser.add_argument('height', type=int)
    args = parser.parse_args(argv)
    return args

def main(argv):
    args = parse_args(argv[1:], prog=argv[0])

    bsp = tcod.bsp.BSP(0, 0, args.width, args.height)
    bsp.split_recursive(
        depth=3,
        min_width=5, min_height=5,
        max_vertical_ratio=1.5, max_horizontal_ratio=1.5
    )

    node_names = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    current_node_name_index = 0

    print('digraph {')

    for node in bsp.post_order():
        try:
            node_name = getattr(node, 'viz_name')
        except AttributeError:
            node_name = node_names[current_node_name_index]
            setattr(node, 'viz_name', node_name)

            bounds = (node.x, node.y, node.width, node.height)
            print(f'  {node_name} [label=\"{current_node_name_index}: {bounds}\"]')

            current_node_name_index += 1

        if node.children:
            node_name = getattr(node, 'viz_name')
            left_child_name = getattr(node.children[0], 'viz_name')
            right_child_name = getattr(node.children[1], 'viz_name')
            print(f'  {node_name} -> {left_child_name}')
            print(f'  {node_name} -> {right_child_name}')

    print('}')

if __name__ == '__main__':
    import sys
    result = main(sys.argv)
    sys.exit(0 if not result else result)
