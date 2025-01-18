import time
import cv2
import numpy as np
from adbutils import adb
from PIL import Image
import io

class DouYinAutoHelper:
    def __init__(self):
        # 连接设备
        self.device = adb.device()
        
    def get_screen_shot(self):
        # 获取屏幕截图并转换格式
        screen = self.device.screenshot()
        # 将 PIL Image 转换为 opencv 格式
        screen = np.array(screen)
        # 转换颜色空间从 RGB 到 BGR
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        return screen
    
    def find_and_click(self, template_path, threshold=0.8):
        try:
            # 图像识别并点击
            screen = self.get_screen_shot()
            template = cv2.imread(template_path)
            
            if template is None:
                print(f"无法读取模板图片: {template_path}")
                return False
                
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)
            
            if len(loc[0]) > 0:
                # 获取匹配位置的中心点
                pt = (loc[1][0] + template.shape[1]//2, loc[0][0] + template.shape[0]//2)
                # 点击屏幕
                self.device.click(pt[0], pt[1])
                return True
            return False
        except Exception as e:
            print(f"在find_and_click中发生错误: {e}")
            return False
    
    def check_go_receive(self, template_path, threshold=0.8):
        try:
            # 检查"去领取"是否出现
            screen = self.get_screen_shot()
            template = cv2.imread(template_path)
            
            if template is None:
                print(f"无法读取模板图片: {template_path}")
                return False
                
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)
            return len(loc[0]) > 0
        except Exception as e:
            print(f"在check_go_receive中发生错误: {e}")
            return False
    
    def run(self):
        print("程序开始运行...")
        while True:
            try:
                # 首先检查是否显示"去领取"
                if self.check_go_receive('templates/go_receive.png'):
                    print("检测到'去领取'按钮！程序停止。")
                    return  # 直接返回，结束程序
                
                # 点击抖一抖
                if self.find_and_click('templates/shake_button.png'):
                    print("点击抖一抖")
                    # 等待10秒，期间每秒检查一次"去领取"是否出现
                    for _ in range(10):
                        if self.check_go_receive('templates/go_receive.png'):
                            print("检测到'去领取'按钮！程序停止。")
                            return  # 直接返回，结束程序
                        time.sleep(1)
                
                # 等待并点击"做饭成功，去领红包"
                if self.find_and_click('templates/cooking_success.png'):
                    print("点击做饭成功按钮")
                    time.sleep(2)
                    
                    # 检查"去领取"
                    if self.check_go_receive('templates/go_receive.png'):
                        print("检测到'去领取'按钮！程序停止。")
                        return  # 直接返回，结束程序
                
                # 点击开心收下
                if self.find_and_click('templates/accept_bonus.png'):
                    print("点击开心收下")
                    time.sleep(2)
                    
                    # 检查"去领取"
                    if self.check_go_receive('templates/go_receive.png'):
                        print("检测到'去领取'按钮！程序停止。")
                        return  # 直接返回，结束程序
                
            except Exception as e:
                print(f"发生错误: {e}")
                time.sleep(1)

if __name__ == "__main__":
    helper = DouYinAutoHelper()
    helper.run()