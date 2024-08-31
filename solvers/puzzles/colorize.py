class Color:
    BLACK = '\033[30m'  # (文字)黒
    RED = '\033[31m'  # (文字)赤
    GREEN = '\033[32m'  # (文字)緑
    YELLOW = '\033[33m'  # (文字)黄
    BLUE = '\033[34m'  # (文字)青
    MAGENTA = '\033[35m'  # (文字)マゼンタ
    CYAN = '\033[36m'  # (文字)シアン
    WHITE = '\033[37m'  # (文字)白
    COLOR_DEFAULT = '\033[39m'  # 文字色をデフォルトに戻す
    BOLD = '\033[1m'  # 太字
    UNDERLINE = '\033[4m'  # 下線
    INVISIBLE = '\033[08m'  # 不可視
    REVERSE = '\033[07m'  # 文字色と背景色を反転
    BG_BLACK = '\033[40m'  # (背景)黒
    BG_RED = '\033[41m'  # (背景)赤
    BG_GREEN = '\033[42m'  # (背景)緑
    BG_YELLOW = '\033[43m'  # (背景)黄
    BG_BLUE = '\033[44m'  # (背景)青
    BG_MAGENTA = '\033[45m'  # (背景)マゼンタ
    BG_CYAN = '\033[46m'  # (背景)シアン
    BG_WHITE = '\033[47m'  # (背景)白
    BG_DEFAULT = '\033[49m'  # 背景色をデフォルトに戻す
    RESET = '\033[0m'  # 全てリセット

if __name__ == '__main__':
    print(f'黒:{Color.BLACK}●ABC{Color.RESET}')
    print(f'赤:{Color.RED}●ABC{Color.RESET}')
    print(f'緑:{Color.GREEN}●ABC{Color.RESET}')
    print(f'黄:{Color.YELLOW}●ABC{Color.RESET}')
    print(f'青:{Color.BLUE}●ABC{Color.RESET}')
    print(f'マゼンタ:{Color.MAGENTA}●ABC{Color.RESET}')
    print(f'シアン:{Color.CYAN}●ABC{Color.RESET}')
    print(f'白:{Color.WHITE}●ABC{Color.RESET}')
    print(f'下線:{Color.UNDERLINE}●ABC{Color.RESET}')
    print(f'太字:{Color.BOLD}●ABC{Color.RESET}')
    print(f'不可視:{Color.INVISIBLE}●ABC{Color.RESET}')
    print(f'反転:{Color.REVERSE}●ABC{Color.RESET}')
    print(f'背景黒:{Color.BG_BLACK}●ABC{Color.RESET}')
    print(f'背景赤:{Color.BG_RED}●ABC{Color.RESET}')
    print(f'背景緑:{Color.BG_GREEN}●ABC{Color.RESET}')
    print(f'背景黄:{Color.BG_YELLOW}●ABC{Color.RESET}')
    print(f'背景青:{Color.BG_BLUE}●ABC{Color.RESET}')
    print(f'背景マゼンタ:{Color.BG_MAGENTA}●ABC{Color.RESET}')
    print(f'背景シアン:{Color.BG_CYAN}●ABC{Color.RESET}')
    print(f'背景白:{Color.BG_WHITE}●ABC{Color.RESET}')
    # 文字色と背景色を変える
    print(f'文字赤+背景緑:{Color.RED}{Color.BG_GREEN}●ABC{Color.RESET}')