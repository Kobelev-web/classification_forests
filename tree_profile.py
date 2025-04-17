import os
import geopandas as gpd
import laspy
import numpy as np
import matplotlib.pyplot as plt

def add_las_attributes_and_plot(output_crowns_shp, input_cropped_folder, output_cropped_folder, output_tree_profile_folder):
    # Загрузка SHP-файла
    crowns_gdf = gpd.read_file(output_crowns_shp)

    # Проверка наличия необходимых атрибутов
    if 'tree_id' not in crowns_gdf.columns:
        raise ValueError("Входной SHP-файл должен содержать атрибут 'tree_id'!")

    # Создание нового столбца для высоты дерева из LAS-файла
    crowns_gdf['height_tree_las'] = None

    # Создание папки для сохранения графиков
    os.makedirs(output_tree_profile_folder, exist_ok=True)

    # Обработка каждого дерева
    for idx, row in crowns_gdf.iterrows():
        tree_id = row['tree_id']
        las_file_name = f"{tree_id}.las"
        las_file_path = os.path.join(input_cropped_folder, las_file_name)

        # Проверка существования LAS-файла
        if not os.path.exists(las_file_path):
            print(f"LAS-файл для дерева с ID {tree_id} не найден. Пропускаем.")
            continue

        # Чтение LAS-файла
        try:
            las = laspy.read(las_file_path)
        except Exception as e:
            print(f"Ошибка при чтении LAS-файла для дерева с ID {tree_id}: {e}")
            continue

        # Извлечение координат
        x = las.x
        y = las.y
        z = las.z

        # Расчет высоты дерева
        height_tree_las = z.max() - z.min()

        # Запись значения высоты в GeoDataFrame
        crowns_gdf.at[idx, 'height_tree_las'] = height_tree_las

        print(f"Обработано дерево с ID {tree_id}: height_tree_las={height_tree_las:.2f}")

        # 1. Вид сбоку (XZ)
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.scatter(x, z, s=1, c='green', alpha=0.5)
        ax1.set_title("Side View (XZ)")
        ax1.set_xlabel("X (м)")
        ax1.set_ylabel("Z (м) - Height")
        ax1.grid(True)
        ax1.set_aspect('equal')  # Равный масштаб

        # Сохранение первого графика
        output_image_path_1 = os.path.join(output_tree_profile_folder, f"{tree_id}_1.png")
        fig1.savefig(output_image_path_1, dpi=300)
        print(f"График сохранен: {output_image_path_1}")

        # Очистка памяти после создания графика
        plt.close(fig1)

        # 2. Вид сбоку (YZ)
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.scatter(y, z, s=1, c='purple', alpha=0.5)
        ax2.set_title("Side View (YZ)")
        ax2.set_xlabel("Y (м)")
        ax2.set_ylabel("Z (м) - Height")
        ax2.grid(True)
        ax2.set_aspect('equal')  # Равный масштаб

        # Сохранение второго графика
        output_image_path_2 = os.path.join(output_tree_profile_folder, f"{tree_id}_2.png")
        fig2.savefig(output_image_path_2, dpi=300)
        print(f"График сохранен: {output_image_path_2}")

        # Очистка памяти после создания графика
        plt.close(fig2)

    # Сохранение обновленного SHP-файла
    crowns_gdf.to_file(output_cropped_folder, driver="ESRI Shapefile")
    print(f"Обновленный SHP-файл сохранен: {output_cropped_folder}")

# Пример использования
if __name__ == "__main__":
    output_crowns_shp = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"
    input_cropped_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud Crop"
    output_cropped_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_height_las.shp"
    output_tree_profile_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Tree_profile"

    add_las_attributes_and_plot(output_crowns_shp, input_cropped_folder, output_cropped_folder, output_tree_profile_folder)