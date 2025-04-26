import sys, json
import Slither


def main():
    payload = json.load(sys.stdin)
    height = payload['height']
    width = payload['width']
    problem = payload['problem']

    # ソルバー実行
    is_sat, grid = Slither.solve_slitherlink_variant(height, width, problem)
    horizontal = []
    vertical = []


    def sol_to_str(sol, is_sat):
        if not  is_sat:
            return 2
        if sol is None:
            return 0
        if sol == True:
            return 1
        if sol == False:
            return 2

    for y in range(height+1):
        line = []
        for x in range(width): 
            line.append(sol_to_str(grid.horizontal[y, x].sol, is_sat))
        horizontal.append(line)
    
    
    for y in range(height):
        line = []
        for x in range(width+1):
            line.append(sol_to_str(grid.vertical[y, x].sol, is_sat))
        vertical.append(line)
    
    # JSON で出力
    print(json.dumps({
        'horizontal': horizontal,
        'vertical': vertical
    }))
    
    # 自身を終了 
    sys.exit(0)


if __name__ == '__main__':
    main()
