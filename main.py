import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")

        # API ключ из переменных окружения
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not self.api_key:
            messagebox.showerror("Ошибка", "API ключ не найден! Создайте файл .env с EXCHANGE_RATE_API_KEY=ваш_ключ")

        # Файл для сохранения истории
        self.history_file = "conversion_history.json"
        self.history = []
        self.load_history()

        self.setup_ui()
        self.update_currencies()

    def setup_ui(self):
        # Форма конвертации
        input_frame = ttk.LabelFrame(self.root, text="Конвертация валют")
        input_frame.pack(pady=10, padx=20, fill="x")

        # Выбор валюты «из»
        ttk.Label(input_frame, text="Из:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_currency = ttk.Combobox(input_frame, width=10)
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)

        # Выбор валюты «в»
        ttk.Label(input_frame, text="В:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.to_currency = ttk.Combobox(input_frame, width=10)
        self.to_currency.grid(row=0, column=3, padx=5, pady=5)

        # Поле ввода суммы
        ttk.Label(input_frame, text="Сумма:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка конвертации
        convert_btn = ttk.Button(input_frame, text="Конвертировать", command=self.convert_currency)
        convert_btn.grid(row=1, column=2, columnspan=2, pady=10)

        # Результат конвертации
        result_frame = ttk.LabelFrame(self.root, text="Результат")
        result_frame.pack(pady=10, padx=20, fill="x")
        self.result_label = ttk.Label(result_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        # История конвертаций
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций")
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        self.history_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_history_list()

    def update_currencies(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            if response.status_code == 200:
                data = response.json()
                currencies = list(data["rates"].keys())
                self.from_currency["values"] = currencies
                self.to_currency["values"] = currencies
                # Устанавливаем значения по умолчанию
                self.from_currency.set("USD")
                self.to_currency.set("EUR")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {str(e)}")

    def validate_input(self, amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return False, 0
            return True, amount
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
            return False, 0

    def convert_currency(self):
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        amount_str = self.amount_entry.get().strip()

        is_valid, amount = self.validate_input(amount_str)
        if not is_valid:
            return

        try:
            # Получаем курс через API
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_curr}")
            if response.status_code != 200:
                messagebox.showerror("Ошибка", "Не удалось получить курс валют!")
                return

            data = response.json()
            rate = data["rates"][to_curr]
            result = amount * rate

            # Отображаем результат
            self.result_label.config(text=f"{amount} {from_curr} = {result:.2f} {to_curr}")

            # Сохраняем в историю
            record = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "from": from_curr,
                "to": to_curr,
                "result": round(result, 2)
            }
            self.history.append(record)
            self.save_history()
            self.update_history_list()
        except KeyError:
            messagebox.showerror("Ошибка", "Некорректные валюты!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def update_history_list(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for record in reversed(self.history[-10:]):  # Последние 10 записей
            self.history_tree.insert("", "end", values=(
                record["date"], record["amount"],
                record["from"], record["to"], record["result"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
