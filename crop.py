import os
import laspy
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

def crop_point_cloud_by_polygons(input_shp_path, input_las_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Загрузка SHP-файла крон деревьев
    polygons_gdf = gpd.read_file(input_shp_path)
    if 'tree_id' not in polygons_gdf.columns:
        raise ValueError("Входной SHP-файл должен содержать атрибут 'tree_id'!")

    # Чтение LAS-файла
    las = laspy.read(input_las_path)  # Прямое чтение без использования with
    points = np.vstack((las.x, las.y, las.z)).T  # Массив точек (x, y, z)

    # Функция для проверки, находится ли точка внутри полигона
    def is_point_in_polygon(point, polygon):
        return polygon.contains(Point(point[0], point[1]))

    # Обработка каждого полигона
    for _, row in polygons_gdf.iterrows():
        tree_id = row['tree_id']
        polygon = row['geometry']

        # Фильтрация точек внутри полигона
        filtered_points = [point for point in points if is_point_in_polygon(point, polygon)]

        if len(filtered_points) == 0:
            print(f"Предупреждение: Нет точек для дерева с ID {tree_id}. Пропускаем.")
            continue

        # Преобразование отфильтрованных точек в формат LAS
        filtered_points = np.array(filtered_points)
        new_las = laspy.create()
        new_las.x = filtered_points[:, 0]
        new_las.y = filtered_points[:, 1]
        new_las.z = filtered_points[:, 2]

        # Сохранение LAS-файла
        output_las_path = os.path.join(output_folder, f"{tree_id}.las")
        new_las.write(output_las_path)  # Используем write вместо with
        print(f"Сохранено облако точек для дерева с ID {tree_id}: {output_las_path}")

# Пример использования
if __name__ == "__main__":
    input_shp_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"
    input_las_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud\Cloud.las"
    output_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud Crop"

    crop_point_cloud_by_polygons(input_shp_path, input_las_path, output_folder)