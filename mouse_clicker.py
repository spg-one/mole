# 烧菜流程（run_mode）说明：
# 第一段，每个炉灶选菜：
#   P1(点击) -> 3s -> Pm(点击) -> 1.5s
#   P2(点击) -> 3s -> Pm(点击) -> 1.5s
#   ...
#   P7(点击) -> 3s -> Pm(点击) -> 1.5s
# 第二段，每个炉灶点两次：
#   P1(点击) -> 1.5s -> P2(点击) -> 1.5s -> ... -> P7(点击) -> 1.5s
#   P1(点击) -> 1.5s -> P2(点击) -> 1.5s -> ... -> P7(点击) -> 1.5s
# 等待t秒（每1分钟输出剩余时间并点击Pc一次）
# 保险延时5秒
# 第三段，每个炉灶收菜：
#   P1(点击) -> 3s -> P2(点击) -> 3s -> ... -> P7(点击) -> 3s
# 本轮结束后延时3秒，循环下一轮

import pyautogui
import keyboard
import time
import json
import os
import re

def parse_interval(interval_str):
    match = re.match(r"(\d+)([hm])", interval_str.strip().lower())
    if not match:
        raise ValueError("Invalid interval format. Use like '1h' or '30m'.")
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'h':
        return value * 3600
    else:
        return value * 60


def record_p1p7(config_path):
    print("请依次将鼠标移动到7个点位（P1-P7），每次移动后按空格键记录。")
    points = []
    for i in range(7):
        print(f"请将鼠标移动到第{i+1}个点位，然后按空格键记录...")
        while not keyboard.is_pressed('space'):
            pass
        pos = pyautogui.position()
        print(f"已记录点位{i+1}: {pos}")
        points.append([pos.x, pos.y])
        while keyboard.is_pressed('space'):
            pass
    # 保存到config.json
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except Exception:
                config = {}
    config['p1p7'] = points
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("P1-P7点位已保存到 config.json")

def record_pm(config_path):
    print("请将鼠标移动到Pm点位，然后按空格键记录...")
    while not keyboard.is_pressed('space'):
        pass
    pos = pyautogui.position()
    print(f"已记录点位Pm: {pos}")
    # 保存到config.json
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except Exception:
                config = {}
    config['pm'] = [pos.x, pos.y]
    interval = input("请输入时间间隔t（如1h或30m）：")
    config['interval'] = interval
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("Pm点位和时间间隔已保存到 config.json")

def run_mode(config_path):
    if not os.path.exists(config_path):
        print(f"配置文件 {config_path} 不存在，请先运行记录模式。")
        return
    # 读取config.json
    if not os.path.exists('config.json'):
        print('未找到config.json，请先记录P1-P7和Pm点位！')
        return
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    if 'p1p7' not in config or len(config['p1p7']) != 7:
        print('config.json中P1-P7点位不正确，请先记录P1-P7点位！')
        return
    if 'pm' not in config or len(config['pm']) != 2:
        print('config.json中Pm点位不正确，请先记录Pm点位！')
        return
    if 'interval' not in config:
        interval = input('config.json中未找到时间间隔，请输入（如1h或30m）：')
        config['interval'] = interval
        with open('config.json', 'w', encoding='utf-8') as f2:
            json.dump(config, f2, ensure_ascii=False, indent=2)
    P = config['p1p7']
    Pm = config['pm']
    interval = parse_interval(config['interval'])

    # 启动倒计时
    print("即将开始自动点击，5秒后启动，请切换到目标窗口准备...")
    for i in range(5, 0, -1):
        print(f"{i}...", end='', flush=True)
        time.sleep(1)
        
    # 读取Pc（如有）
    Pc = None
    if 'pc' in config and len(config['pc']) == 2:
        Pc = config['pc']

    while True:    
        print("\n开始点击... 第一段")
        for i in range(7):
            pyautogui.click(P[i][0], P[i][1])
            time.sleep(3)
            pyautogui.click(Pm[0], Pm[1])
            time.sleep(1.5)
        # 第二段：P1,1s,P2,1s,...
        print("开始点击... 第二段")
        for i in range(7):
            pyautogui.click(P[i][0], P[i][1])
            time.sleep(1.5)
        for i in range(7):
            pyautogui.click(P[i][0], P[i][1])
            time.sleep(1.5)
        print(f"等待{interval}秒...（等待期间可输入新间隔t，回车确认修改）")
        start_time = time.time()
        waited = 0
        last_print = 0
        while waited < interval:
            waited = time.time() - start_time
            time_left = interval - waited
            # 每60秒输出一次剩余时间，并点击Pc
            if int(waited) - last_print >= 60 or waited == 0:
                print(f"剩余等待时间：{int(time_left)}秒。输入新t(如1h/30m/120s)并回车可修改，直接回车继续等待...")
                last_print = int(waited)
                if Pc:
                    pyautogui.click(Pc[0], Pc[1])
            # 检查输入
            if keyboard.is_pressed('enter'):
                new_t = input("请输入新的等待时间t（如1h/30m/120s）：").strip()
                if new_t:
                    m = re.match(r"(\d+)([hms])", new_t.lower())
                    if not m:
                        print("格式错误，继续等待...")
                        continue
                    v, u = int(m.group(1)), m.group(2)
                    if u == 'h':
                        new_interval = v * 3600
                    elif u == 'm':
                        new_interval = v * 60
                    else:
                        new_interval = v
                    if new_interval < waited:
                        print(f"新t({new_interval}s)小于已等待时间({int(waited)}s)，不允许修改！")
                    else:
                        interval = new_interval
                        print(f"已修改等待时间t为{new_t}，剩余{int(interval-waited)}秒。")
            time.sleep(1)
        print("保险延时5秒...")
        time.sleep(5)
        # 第三段：P1,2s,P2,2s,...
        print("开始点击... 第三段")
        for i in range(7):
            pyautogui.click(P[i][0], P[i][1])
            time.sleep(3)
        print("本轮点击流程完成，2秒后进入下一轮...（Ctrl+C可终止）")
        time.sleep(3)
def record_pc(config_path):
    print("请将鼠标移动到中心点Pc，然后按空格键记录...")
    while not keyboard.is_pressed('space'):
        pass
    pos = pyautogui.position()
    print(f"已记录中心点Pc: {pos}")
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except Exception:
                config = {}
    config['pc'] = [pos.x, pos.y]
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("中心点Pc已保存到 config.json")

def main():
    config_path = 'config.json'  # 兼容参数
    print("请选择模式：1-开始烧菜 2-记录菜品位置和时间 3-记录炉灶位置 4-记录确认位置")
    print("1-开始烧菜（执行自动点击流程）\n2-记录菜品位置和时间（记录Pm和t）\n3-记录炉灶位置（记录P1-P7）\n4-记录确认位置（记录Pc）")
    mode = input("输入1/2/3/4：")
    if mode == '1':
        run_mode(config_path)
    elif mode == '2':
        record_pm(config_path)
    elif mode == '3':
        record_p1p7(config_path)
    elif mode == '4':
        record_pc(config_path)
    else:
        print("无效输入！")

if __name__ == "__main__":
    main()
