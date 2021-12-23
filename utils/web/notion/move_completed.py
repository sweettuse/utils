import sys
from concurrent.futures import ThreadPoolExecutor, wait

from misty_py.utils import json_obj
from utils.web.notion import Pages, get, find_key, Block, CopyError


def move_to_completed(page: Pages):
    blocks = get(page.blocks)
    to_move = []
    completed_id = None
    for b in map(json_obj, blocks):
        if find_key(b, 'plain_text') == 'completed:':
            completed_id = b.id
            break
        b = Block.from_id(b.id)
        if b.is_completed():
            to_move.append(b)

    if not completed_id:
        raise Exception(f'Unable to find completed block for {page.name!r}')

    for b in to_move:
        try:
            b.copy_to(completed_id)
            b.delete()
        except CopyError as e:
            print(page.name, type(e), str(e))


def move_all_completeds():
    pool = ThreadPoolExecutor(min(len(Pages), 8))
    futures = [pool.submit(move_to_completed, p) for p in Pages]
    wait(futures)


def __main():
    # move_to_completed(Pages.work_todo)
    move_all_completeds()


def _run_cli():
    """if exactly 2 args, second should be block id to download/print"""
    if len(sys.argv) != 2:
        return False
    # https://www.notion.so/sweettuse/coding-questions-05d955889a4e449f9df3e9810d0eb768#7d8befe9ca6143a3a0df89e44e6eea7c
    link = sys.argv[1]
    block_id = link.rsplit('-', 1)[1].split('#')[-1]
    print(block_id)
    print(Block.from_id(block_id).pretty)
    return True


if __name__ == '__main__':
    # TODO: add date separator for each run if blocks exist
    if not _run_cli():
        __main()
