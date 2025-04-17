import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
from config import k

def create_crown_polygons_with_attributes(input_points_path, output_polygons_path, k=None):
    """
    Создает полигоны крон деревьев на основе точек вершин деревьев и добавляет атрибуты из точечного слоя.

    :param input_points_path: Путь к входному файлу точек (Shapefile или GeoJSON).
    :param output_polygons_path: Путь для сохранения выходного файла полигонов.
    :param k: Коэффициент для расчета диаметра кроны (диаметр = k * высота). Если None, берется из config.py.
    """
    if k is None:
        k = globals()['k']

    # Загрузка точечного слоя
    points_gdf = gpd.read_file(input_points_path)
    
    # Проверка наличия необходимых атрибутов
    required_columns = {'tree_id', 'height', 'x_coord', 'y_coord'}
    if not required_columns.issubset(points_gdf.columns):
        raise ValueError(f"Входной файл должен содержать атрибуты: {required_columns}!")

    # Функция для создания круга
    def create_circle(center, radius, num_segments=36):
        """
        Создает круг с заданным центром и радиусом.

        :param center: Центр круга (tuple с координатами X и Y).
        :param radius: Радиус круга.
        :param num_segments: Количество сегментов для аппроксимации круга.
        :return: Полигон, представляющий круг.
        """
        angles = np.linspace(0, 2 * np.pi, num_segments, endpoint=False)
        circle_coords = [
            (center.x + radius * np.cos(angle), center.y + radius * np.sin(angle))
            for angle in angles
        ]
        return Polygon(circle_coords)

    # Создание полигонов крон
    polygons = []
    for _, row in points_gdf.iterrows():
        tree_id = row['tree_id']  # ID дерева
        height = row['height']    # Высота дерева
        x_coord = row['x_coord']  # Координата X
        y_coord = row['y_coord']  # Координата Y
        diameter = k * height     # Диаметр кроны
        radius = diameter / 2     # Радиус кроны

        # Создание круга
        point = Point(x_coord, y_coord)  # Точка вершины дерева
        circle = create_circle(point, radius)

        # Добавление атрибутов
        polygons.append({
            'geometry': circle,
            'tree_id': tree_id,
            'x_coord': x_coord,
            'y_coord': y_coord,
            'height': height,
            'diameter': diameter
        })

    # Создание GeoDataFrame для полигонов
    polygons_gdf = gpd.GeoDataFrame(polygons, crs=points_gdf.crs)

    # Сохранение полигонов в файл
    polygons_gdf.to_file(output_polygons_path, driver="ESRI Shapefile")
    print(f"Полигоны крон деревьев сохранены: {output_polygons_path}")

# Пример использования
if __name__ == "__main__":
    input_points_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_tops.shp"
    output_polygons_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"

    # Если k не передан, будет использовано значение из config.py
    create_crown_polygons_with_attributes(input_points_path, output_polygons_path)