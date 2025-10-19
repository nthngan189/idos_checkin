
import argparse
from selenium.webdriver.common.by import By
from browser_automation import BrowserManager, Node
from utils import Utility

PROJECT_URL = "https://app.idos.network/idos-profile"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        self.node.go_to(f'https://app.idos.network?ref=3F2D39B9', method="get")
        Utility.wait_time(10)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')

    def is_login(self):
        header_element = self.node.find(By.XPATH, '//header[contains(@class, "flex")]')
        wallet = self.node.get_text(By.XPATH, './/div[contains(@class,"gap-2")]', header_element)
        verify_wallet = self.node.get_text(By.XPATH, './/div[contains(@class,"rounded-sm")]', header_element)
        if wallet and verify_wallet == 'Verified':
            self.node.log(f'Đã login với ví: {wallet}')
            return True
        elif verify_wallet != 'Verified':
            self.node.snapshot(f'Chưa verify ví')
        else:
            self.node.log(f'Chưa login, comfirm login')
        return False

    def login(self):
        check_login = self.is_login()
        if check_login == False:
            Utility.wait_time(10)
            return self.is_login()
        elif check_login == True:
            return check_login

    def check_in(self):
        task = {}
        main_element = self.node.find(By.XPATH, '//main[contains(@class,"flex-1")]')
        inpoint = self.node.get_text(By.XPATH, './/div[contains(@class,"text-3xl")]', main_element)
        quest_element = self.node.find(By.XPATH, './/div[contains(@class,"overflow-y-auto")]', main_element)
        social_element = self.node.find(By.XPATH, './/div[contains(@class,"gap-6") and contains(normalize-space(.), "Social Points")]', main_element)
        contribution_element = self.node.find(By.XPATH, './/div[contains(@class,"gap-6") and contains(normalize-space(.), "Contribution Points")]', main_element)
        task["quest"] = len(self.node.find_all(By.XPATH, './/td[contains(@class,"pr-8") and contains(normalize-space(.), "To do")]', quest_element))
        task["social"] = len(self.node.find_all(By.XPATH, './/button[@type = "button"]', social_element))
        if self.node.find_and_click(By.XPATH, './/td[contains(@class,"cursor-pointer") and normalize-space(.) = "Daily check"]', quest_element):
            Utility.wait_time(2)
            self.node.find_and_click(By.XPATH, '//button[contains(@class,"tracking-wide") and normalize-space(.) = "Check in"]')
            Utility.wait_time(2)
            outpoint = self.node.get_text(By.XPATH, './/div[contains(@class,"text-3xl")]', main_element)
            task["point"] = outpoint
            task["plus"] = float(outpoint) - float(inpoint)
            return task
        else:
            return False
    def _run(self):
        self.node.go_to(f'{PROJECT_URL}', method="get")
        Utility.wait_time(5)
        self.node.find_and_click(By.XPATH, '//a[contains(@class,"cursor-pointer")]')
        if self.login():
            checkin = self.check_in()
            if not checkin:
                self.node.snapshot(f'Check-in thất bại')
            self.node.snapshot(f'Point: {checkin["point"]}, Plus: {checkin["plus"]}, Quest: {checkin["quest"]}, Social: {checkin["social"]}')
        else:
            self.node.snapshot(f'Login thất bại')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name')
    max_profiles = Utility.read_config('MAX_PROFLIES')
    max_profiles = int(max_profiles[0]) if max_profiles else 4
    
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    # browser_manager.config_extension('Meta-Wallet-*.crx','OKX-Wallet-*.crx')
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
    )