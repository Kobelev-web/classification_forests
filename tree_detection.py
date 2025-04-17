import numpy as np
from scipy.ndimage import maximum_filter, minimum_filter, label
from skimage.segmentation import watershed
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import xy
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN  # Добавляем импорт DBSCAN

def align_rasters(source_path, target_path):
    """
    Выравнивание растров: изменение размера и разрешения source_path под target_path.
    """
    with rasterio.open(source_path) as src, rasterio.open(target_path) as tgt:
        # Создаем массив для нового растра
        aligned_data = np.zeros(tgt.shape, dtype=src.dtypes[0])
        
        # Выполняем репроекцию (ресемплинг)
        reproject(
            source=rasterio.band(src, 1),  # Исходный растр
            destination=aligned_data,      # Целевой массив
            src_transform=src.transform,   # Географическая привязка исходного растра
            src_crs=src.crs,               # Система координат исходного растра
            dst_transform=tgt.transform,   # Географическая привязка целевого растра
            dst_crs=tgt.crs,               # Система координат целевого растра
            resampling=Resampling.bilinear # Метод интерполяции
        )
        
        return aligned_data, tgt.transform, tgt.crs

def find_tree_tops_with_coords():
    # Пути к растрам
    relief_raster_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF рельеф\relief_raster.tif"
    trees_raster_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF лес\Cloud_smoothed.tif"

    # Чтение данных рельефа
    with rasterio.open(relief_raster_path) as relief_src:
        relief_data = relief_src.read(1)
        relief_transform = relief_src.transform
        relief_crs = relief_src.crs
        relief_no_data = relief_src.nodata

    # Чтение данных деревьев
    with rasterio.open(trees_raster_path) as trees_src:
        trees_data = trees_src.read(1)
        trees_transform = trees_src.transform
        trees_crs = trees_src.crs
        trees_no_data = trees_src.nodata

    # Выравнивание растров
    if relief_data.shape != trees_data.shape:
        print("Размеры растров различаются. Выполняется выравнивание...")
        trees_data, trees_transform, trees_crs = align_rasters(trees_raster_path, relief_raster_path)

    # Замена NoData значений на NaN
    relief_data[relief_data == relief_no_data] = np.nan
    trees_data[trees_data == trees_no_data] = np.nan

    # Вычисление высоты деревьев
    height_data = trees_data - relief_data
    height_data[height_data < 0] = np.nan  # Игнорируем отрицательные значения

    # Проверка количества отрицательных значений
    negative_pixels = np.sum(height_data < 0)
    print(f"Количество пикселей с отрицательной высотой: {negative_pixels}")

    # Автоматическая настройка параметров
    resolution = max(relief_transform[0], -relief_transform[4]) or 0.5
    valid_heights = height_data[~np.isnan(height_data)]
    if len(valid_heights) == 0:
        raise ValueError("Растр не содержит допустимых значений высот!")

    avg_height = np.nanmean(valid_heights)
    std_height = np.nanstd(valid_heights)

    # Определение размера блока
    block_size = 1000

    # Список для хранения всех найденных вершин
    all_points = []

    # Обработка данных блоками
    for y in range(0, height_data.shape[0], block_size):
        for x in range(0, height_data.shape[1], block_size):
            # Извлечение блока
            block = height_data[y:y + block_size, x:x + block_size]

            # Предварительная обработка блока
            smoothed = maximum_filter(block, size=2)  # Уменьшаем размер фильтра
            smoothed = minimum_filter(smoothed, size=2)

            # Поиск локальных максимумов
            window_size = max(2, int(1 / resolution))  # Уменьшаем размер окна
            local_max = (smoothed == maximum_filter(smoothed, size=window_size))
            threshold = max(avg_height - 0.2 * std_height, np.nanmin(block))  # Уменьшаем порог

            # Создаем маркеры для водораздела
            markers = local_max.astype(int)
            labels = watershed(-smoothed, markers, mask=~np.isnan(block))

            # Фильтрация кандидатов
            candidates = np.where(labels > 0)

            # Подготовка данных о вершинах
            for cy, cx in zip(*candidates):
                px, py = xy(relief_transform, y + cy, x + cx)  # Преобразование индексов пикселей в координаты
                all_points.append({
                    'geometry': Point(px, py),
                    'height': round(block[cy, cx], 1),  # Округляем высоту до десятых
                    'x_coord': round(px, 1),           # Округляем координаты до десятых
                    'y_coord': round(py, 1)
                })

    # Создание GeoDataFrame из всех найденных точек
    gdf = gpd.GeoDataFrame(all_points, crs=relief_crs)

    # Пространственная фильтрация с использованием DBSCAN
    coords = np.column_stack((gdf['x_coord'], gdf['y_coord']))  # Формируем массив координат
    clustering = DBSCAN(eps=resolution * 3, min_samples=5).fit(coords)  # Кластеризация
    gdf['cluster'] = clustering.labels_  # Добавляем метки кластеров в GeoDataFrame

    # Фильтрация точек: удаляем шумовые точки (метка -1)
    filtered_gdf = gdf[gdf['cluster'] != -1]

    # Назначение ID деревьев
    confirmed_trees = []
    current_id = 1

    for cluster_id in filtered_gdf['cluster'].unique():
        cluster_points = filtered_gdf[filtered_gdf['cluster'] == cluster_id]
        highest_point = cluster_points.loc[cluster_points['height'].idxmax()]  # Находим самую высокую точку в кластере
        highest_point['tree_id'] = current_id
        confirmed_trees.append(highest_point.to_dict())
        current_id += 1

    # Создание итогового GeoDataFrame
    confirmed_gdf = gpd.GeoDataFrame(confirmed_trees, crs=relief_crs)

    # Сохранение точечного слоя в файл
    output_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_tops.shp"
    confirmed_gdf.to_file(output_path, driver="ESRI Shapefile")

    print(f"Точечный слой сохранен: {output_path}")

    # Вывод статистики
    print(f"Результаты обработки:\n"
          f"• Обнаружено деревьев: {len(confirmed_trees)}\n"
          f"• Средняя высота: {avg_height:.1f} м\n"
          f"• Максимальная высота: {np.nanmax(height_data):.1f} м\n"
          f"• Разрешение: {resolution:.2f} м/пиксель\n"
          f"• Использованный порог: {threshold:.1f} м")

if __name__ == "__main__":
    find_tree_tops_with_coords()