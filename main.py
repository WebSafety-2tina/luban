import requests
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading

class LubanSMS:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://lubansms.com/v2/api"

    def get_keyword_number(self, phone=None, card_type=None):
        url = f"{self.base_url}/getKeywordNumber"
        params = {
            "apikey": self.api_key,
            "phone": phone,
            "cardType": card_type
        }
        response = requests.get(url, params=params)
        return response.json()

    def release_number(self, phone):
        url = f"{self.base_url}/delKeywordNumber"
        params = {
            "apikey": self.api_key,
            "phone": phone
        }
        response = requests.get(url, params=params)
        return response.json()

    def get_keyword_sms(self, phone, keyword):
        url = f"{self.base_url}/getKeywordSms"
        params = {
            "apikey": self.api_key,
            "phone": phone,
            "keyword": keyword
        }
        response = requests.get(url, params=params)
        return response.json()

class Application(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("鲁班接吗平台程序{2tina}")
        self.geometry("800x700")

        self.running = False

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # API Key
        ttk.Label(main_frame, text="API密钥:").grid(row=0, column=0, sticky=W, pady=5)
        self.api_key_entry = ttk.Entry(main_frame, width=40)
        self.api_key_entry.grid(row=0, column=1, pady=5)

        # Phone number
        ttk.Label(main_frame, text="电话号码（留空随机获取）:").grid(row=1, column=0, sticky=W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=40)
        self.phone_entry.grid(row=1, column=1, pady=5)

        # Card type
        ttk.Label(main_frame, text="卡类型:").grid(row=2, column=0, sticky=W, pady=5)
        self.card_type_combobox = ttk.Combobox(main_frame, values=["实卡", "虚卡", "全部"])
        self.card_type_combobox.grid(row=2, column=1, pady=5)
        self.card_type_combobox.current(2)

        # Get number button
        self.get_number_button = ttk.Button(main_frame, text="获取号码", command=self.start_get_number, style='primary.TButton')
        self.get_number_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Keyword
        ttk.Label(main_frame, text="短信关键词:").grid(row=4, column=0, sticky=W, pady=5)
        self.keyword_entry = ttk.Entry(main_frame, width=40)
        self.keyword_entry.grid(row=4, column=1, pady=5)

        # Get SMS button
        self.get_sms_button = ttk.Button(main_frame, text="获取短信", command=self.start_get_sms, style='primary.TButton')
        self.get_sms_button.grid(row=5, column=0, pady=10)

        # Cancel button
        self.cancel_button = ttk.Button(main_frame, text="取消", command=self.cancel_operation, state=DISABLED, style='secondary.TButton')
        self.cancel_button.grid(row=5, column=1, pady=10)

        # Release number
        ttk.Label(main_frame, text="要释放的电话号码:").grid(row=6, column=0, sticky=W, pady=5)
        self.release_entry = ttk.Entry(main_frame, width=40)
        self.release_entry.grid(row=6, column=1, pady=5)

        # Release button
        self.release_button = ttk.Button(main_frame, text="释放号码", command=self.release_number, style='primary.TButton')
        self.release_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Result text
        self.result_text = ttk.Text(main_frame, height=10, width=70)
        self.result_text.grid(row=8, column=0, columnspan=2, pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', length=500)
        self.progress_bar.grid(row=9, column=0, columnspan=2, pady=10)

    def start_get_number(self):
        self.running = True
        self.get_number_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.progress_bar.start()
        threading.Thread(target=self.get_number, daemon=True).start()

    def start_get_sms(self):
        self.running = True
        self.get_sms_button.config(state=DISABLED)
        self.cancel_button.config(state=NORMAL)
        self.progress_bar.start()
        threading.Thread(target=self.get_sms, daemon=True).start()

    def cancel_operation(self):
        self.running = False
        self.get_number_button.config(state=NORMAL)
        self.get_sms_button.config(state=NORMAL)
        self.cancel_button.config(state=DISABLED)
        self.progress_bar.stop()

    def get_number(self):
        api_key = self.api_key_entry.get().strip()
        phone = self.phone_entry.get().strip()
        card_type = self.card_type_combobox.get().strip()

        if not api_key:
            self.show_error("请填写API密钥")
            return

        sms_service = LubanSMS(api_key)

        if card_type not in ["实卡", "虚卡", "全部"]:
            card_type = "全部"

        response = sms_service.get_keyword_number(phone if phone else None, card_type)
        self.update_result(f"获取号码: {response}\n")

        self.cancel_operation()

    def get_sms(self):
        api_key = self.api_key_entry.get().strip()
        phone = self.phone_entry.get().strip()
        keyword = self.keyword_entry.get().strip()

        if not api_key:
            self.show_error("请填写API密钥")
            return

        if not phone:
            self.show_error("请填写电话号码")
            return

        sms_service = LubanSMS(api_key)

        attempts = 0
        while self.running and attempts < 12:  # 最多尝试1分钟（5秒 * 12次）
            sms_response = sms_service.get_keyword_sms(phone, keyword)
            if sms_response["code"] == 0:
                self.update_result(f"获取到短信: {sms_response['msg']}\n")
                break
            else:
                self.update_result("尚未收到短信, 请稍后重试\n")
                time.sleep(5)
                attempts += 1
        if attempts >= 12:
            self.update_result("未能在1分钟内收到短信，操作超时\n")

        self.cancel_operation()

    def release_number(self):
        api_key = self.api_key_entry.get().strip()
        phone = self.release_entry.get().strip()

        if not api_key:
            self.show_error("请填写API密钥")
            return

        if not phone:
            self.show_error("请填写要释放的电话号码")
            return

        sms_service = LubanSMS(api_key)
        release_response = sms_service.release_number(phone)
        self.update_result(f"释放号码: {release_response}\n")

    def update_result(self, message):
        self.result_text.insert(END, message)
        self.result_text.see(END)

    def show_error(self, message):
        self.cancel_operation()
        ttk.Messagebox.show_error(title="错误", message=message)

if __name__ == "__main__":
    app = Application()
    app.mainloop()