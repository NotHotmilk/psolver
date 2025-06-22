#!/usr/bin/env python3
import sys, json
import Slither

def process(payload):
    height  = payload['height']
    width   = payload['width']
    problem = payload['problem']
    # ソルバー実行
    is_sat, grid = Slither.solve_slitherlink_variant(height, width, problem)

    # 解を horizontal/vertical に整形
    horizontal, vertical = [], []
    def sol_to_str(sol, is_sat):
        if not is_sat: return 2
        if sol is None: return 0
        return 1 if sol else 2

    for y in range(height+1):
        horizontal.append([
            sol_to_str(grid.horizontal[y, x].sol, is_sat)
            for x in range(width)
        ])
    for y in range(height):
        vertical.append([
            sol_to_str(grid.vertical[y, x].sol, is_sat)
            for x in range(width+1)
        ])

    # 応答にリクエストIDをそのまま返す
    return {
        'id':      payload.get('id'),
        'horizontal': horizontal,
        'vertical':   vertical
    }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            response = process(payload)
            # JSON を一行にまとめて返して flush
            print(json.dumps(response), flush=True)
        except Exception as e:
            # エラーも JSON で返しておく
            errobj = {'id': payload.get('id'), 'error': str(e)}
            print(json.dumps(errobj), flush=True)

if __name__ == '__main__':
    main()
