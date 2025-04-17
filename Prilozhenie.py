import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import pandas as pd
import geopandas as gpd
import threading
from stage_1_raster_creation import stage_1
from stage_2_tree_detection import stage_2
from stage_3_crown_polygons import stage_3
from stage_4_crop_trees import stage_4
from stage_5_add_attributes import stage_5
from stage_6_classification import stage_6

class ForestTaxationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сегментация и классификация леса")

        # Создание виджетов
        self.create_widgets()

        # DataFrame для хранения данных о деревьях
        self.tree_data = pd.DataFrame(columns=["ID", "X Координата", "Y Координата", "Высота (м)", "Диаметр (м)", "Класс"])

    def create_widgets(self):
        # Заголовок
        ttk.Label(self.root, text="Сегментация и классификация леса", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        # Кнопки для каждого этапа
        ttk.Button(self.root, text="Этап 1: Создание растров", command=lambda: self.run_stage_in_thread(self.run_stage_1)).grid(row=1, column=0, pady=5)
        ttk.Button(self.root, text="Этап 2: Поиск вершин деревьев", command=lambda: self.run_stage_in_thread(self.run_stage_2)).grid(row=1, column=1, pady=5)
        ttk.Button(self.root, text="Этап 3: Построение крон", command=lambda: self.run_stage_in_thread(self.run_stage_3)).grid(row=2, column=0, pady=5)
        ttk.Button(self.root, text="Этап 4: Вырезание деревьев", command=lambda: self.run_stage_in_thread(self.run_stage_4)).grid(row=2, column=1, pady=5)
        ttk.Button(self.root, text="Этап 5: Добавление атрибутов", command=lambda: self.run_stage_in_thread(self.run_stage_5)).grid(row=3, column=0, pady=5)
        ttk.Button(self.root, text="Этап 6: Классификация деревьев", command=lambda: self.run_stage_in_thread(self.run_stage_6)).grid(row=3, column=1, pady=5)

        # Кнопка для выполнения всех этапов
        ttk.Button(self.root, text="Выполнить все этапы", command=lambda: self.run_stage_in_thread(self.run_all_stages)).grid(row=4, column=0, columnspan=2, pady=10)

        # Кнопка для загрузки данных из SHP-файла
        ttk.Button(self.root, text="Загрузить данные из SHP", command=self.load_data_from_shp).grid(row=5, column=0, pady=5)

        # Кнопка для сохранения таблицы
        ttk.Button(self.root, text="Сохранить таблицу", command=self.save_table).grid(row=5, column=1, pady=5)

        # Кнопка для сохранения данных в SHP-файл
        ttk.Button(self.root, text="Сохранить SHP файл", command=self.save_shp).grid(row=6, column=0, pady=5)

        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=10)
        self.log_text.grid(row=7, column=0, columnspan=2, pady=10)

        # Таблица для отображения данных о деревьях
        self.tree_table = ttk.Treeview(self.root, columns=("ID", "X Координата", "Y Координата", "Высота (м)", "Диаметр (м)", "Класс"), show="headings")
        self.tree_table.heading("ID", text="ID")
        self.tree_table.heading("X Координата", text="X Координата (м)")
        self.tree_table.heading("Y Координата", text="Y Координата (м)")
        self.tree_table.heading("Высота (м)", text="Высота (м)")
        self.tree_table.heading("Диаметр (м)", text="Диаметр (м)")
        self.tree_table.heading("Класс", text="Класс")
        self.tree_table.grid(row=8, column=0, columnspan=2, pady=10)

    def log_message(self, message):
        """Добавляет сообщение в текстовое поле логов."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Автоматическая прокрутка вниз
        self.root.update_idletasks()  # Обновление интерфейса

    def update_tree_table(self):
        """Обновляет таблицу с данными о деревьях."""
        for row in self.tree_table.get_children():
            self.tree_table.delete(row)  # Очистка таблицы
        for _, row in self.tree_data.iterrows():
            self.tree_table.insert("", "end", values=(
                row["ID"],
                row["X Координата"],
                row["Y Координата"],
                row["Высота (м)"],
                row["Диаметр (м)"],
                row["Класс"]
            ))

    def load_data_from_shp(self):
        """Загружает данные из SHP-файла."""
        shp_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_class.shp"
        try:
            # Загрузка SHP-файла
            gdf = gpd.read_file(shp_path)

            # Извлечение данных
            self.tree_data = pd.DataFrame({
                "ID": gdf["tree_id"],
                "X Координата": gdf["x_coord"],  # Координата X
                "Y Координата": gdf["y_coord"],  # Координата Y
                "Высота (м)": gdf["height_tre"],  # Учитываем усечение названий столбцов
                "Диаметр (м)": gdf["diameter"],  # Используем диаметр вместо ширины кроны
                "Класс": gdf["tree_class"]
            })

            # Проверка типов данных
            numeric_columns = ["X Координата", "Y Координата", "Высота (м)", "Диаметр (м)"]
            for col in numeric_columns:
                if not pd.api.types.is_numeric_dtype(self.tree_data[col]):
                    self.tree_data[col] = pd.to_numeric(self.tree_data[col], errors="coerce")  # Преобразование в числа

            # Обновление таблицы
            self.update_tree_table()
            messagebox.showinfo("Успех", f"Данные успешно загружены из SHP-файла: {shp_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные из SHP-файла: {e}")

    def save_table(self):
        """Сохраняет таблицу в CSV-файл."""
        if self.tree_data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения.")
            return

        # Выбор папки для сохранения
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Сохранить таблицу как"
        )

        if save_path:
            try:
                # Сохранение данных в CSV
                self.tree_data.to_csv(save_path, index=False, encoding="utf-8-sig", sep=";")
                messagebox.showinfo("Успех", f"Таблица успешно сохранена: {save_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить таблицу: {e}")

    def save_shp(self):
        """Сохраняет данные в SHP-файл."""
        if self.tree_data.empty:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения.")
            return

        # Выбор папки для сохранения
        save_path = filedialog.asksaveasfilename(
            defaultextension=".shp",
            filetypes=[("Shapefile", "*.shp")],
            title="Сохранить SHP файл как"
        )

        if save_path:
            try:
                # Создание GeoDataFrame из DataFrame
                geometry = gpd.points_from_xy(self.tree_data["X Координата"], self.tree_data["Y Координата"])
                gdf = gpd.GeoDataFrame(self.tree_data, geometry=geometry)

                # Сохранение данных в SHP-файл
                gdf.to_file(save_path, driver="ESRI Shapefile", encoding="utf-8")
                messagebox.showinfo("Успех", f"SHP файл успешно сохранен: {save_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить SHP файл: {e}")

    def run_stage_in_thread(self, func):
        """Запускает функцию в отдельном потоке."""
        thread = threading.Thread(target=lambda: self.safe_run(func))
        thread.start()

    def safe_run(self, func):
        """
        Безопасно запускает функцию в отдельном потоке.
        Обрабатывает исключения и выводит сообщения об ошибках в лог.
        """
        try:
            func()
        except Exception as e:
            self.log_message(f"Ошибка при выполнении операции: {e}")

    def run_stage_1(self):
        self.log_message("Начало этапа 1: Создание растров...")
        stage_1()
        self.log_message("Этап 1 завершен.")

    def run_stage_2(self):
        self.log_message("Начало этапа 2: Поиск вершин деревьев...")
        stage_2()
        self.log_message("Этап 2 завершен.")

    def run_stage_3(self):
        self.log_message("Начало этапа 3: Построение крон...")
        stage_3()
        self.log_message("Этап 3 завершен.")

    def run_stage_4(self):
        self.log_message("Начало этапа 4: Вырезание деревьев...")
        stage_4()
        self.log_message("Этап 4 завершен.")

    def run_stage_5(self):
        self.log_message("Начало этапа 5: Добавление атрибутов...")
        stage_5()
        self.log_message("Этап 5 завершен.")

    def run_stage_6(self):
        self.log_message("Начало этапа 6: Классификация деревьев...")
        stage_6()
        self.log_message("Этап 6 завершен.")

        # Загрузка данных из SHP-файла после завершения классификации
        self.load_data_from_shp()
        self.update_tree_table()

    def run_all_stages(self):
        self.log_message("Начало обработки проекта таксации леса...")
        self.run_stage_1()
        self.run_stage_2()
        self.run_stage_3()
        self.run_stage_4()
        self.run_stage_5()
        self.run_stage_6()
        self.log_message("Обработка завершена!")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ForestTaxationApp(root)
    root.mainloop()