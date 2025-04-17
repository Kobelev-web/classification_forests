import os
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
from osgeo import gdal, osr
import laspy
import matplotlib.pyplot as plt

def read_las_file(file_path):
    """
    Чтение данных из .las файла.
    """
    try:
        las = laspy.read(file_path)
        points = np.vstack((las.x, las.y, las.z)).transpose()
        return points
    except Exception as e:
        print(f"Ошибка при чтении .las файла: {e}")
        return None


def create_raster_from_points(points, output_path, pixel_size=0.1, nodata_value=-9999):
    """
    Создание растра из облака точек.
    """
    try:
        # Определение границ облака точек
        min_x, min_y = points[:, 0].min(), points[:, 1].min()
        max_x, max_y = points[:, 0].max(), points[:, 1].max()

        # Вычисление размеров растра
        x_res = int((max_x - min_x) / pixel_size)
        y_res = int((max_y - min_y) / pixel_size)

        # Создание сетки для интерполяции
        grid_x, grid_y = np.meshgrid(
            np.linspace(min_x, max_x, x_res),
            np.linspace(min_y, max_y, y_res)
        )

        # Интерполяция значений атрибута
        grid_z = griddata(
            points[:, :2],  # Координаты X, Y
            points[:, 2],   # Значения высоты
            (grid_x, grid_y),
            method='linear',  # Метод интерполяции
            fill_value=nodata_value
        )

        # Инверсия массива данных по оси Y
        grid_z = np.flipud(grid_z)

        # Сохранение растра в файл GeoTIFF
        driver = gdal.GetDriverByName("GTiff")
        out_raster = driver.Create(output_path, x_res, y_res, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform((min_x, pixel_size, 0, max_y, 0, -pixel_size))

        # Установка системы координат (EPSG:32638)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(32638)  # UTM зона 38N
        out_raster.SetProjection(srs.ExportToWkt())

        # Запись данных в растр
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(grid_z)
        out_band.SetNoDataValue(nodata_value)
        out_band.FlushCache()

        print(f"Растр успешно создан: {output_path}")
        return grid_z, (min_x, max_x, min_y, max_y), pixel_size

    except Exception as e:
        print(f"Ошибка при создании растра: {e}")
        return None


def smooth_raster(input_data, sigma=1.5, nodata_value=-9999):
    """
    Сглаживание растра с использованием гауссовского фильтра.
    Исключает значения NoData из процесса сглаживания.
    """
    # Заменяем NoData значения на np.nan
    valid_mask = input_data != nodata_value
    valid_data = np.where(valid_mask, input_data, np.nan)

    # Применяем гауссовский фильтр
    smoothed_valid = gaussian_filter(valid_data, sigma=sigma, mode='reflect')

    # Восстанавливаем NoData значения
    smoothed_data = np.where(valid_mask, smoothed_valid, nodata_value)
    return smoothed_data


def save_smoothed_raster(data, geo_transform, output_path, nodata_value=-9999):
    """
    Сохранение сглаженного растра в файл GeoTIFF.
    """
    try:
        rows, cols = data.shape
        driver = gdal.GetDriverByName("GTiff")
        out_raster = driver.Create(output_path, cols, rows, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform(geo_transform)

        # Установка системы координат (EPSG:32638)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(32638)  # UTM зона 38N
        out_raster.SetProjection(srs.ExportToWkt())

        # Запись данных в растр
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(data)
        out_band.SetNoDataValue(nodata_value)
        out_band.FlushCache()

        print(f"Сглаженный растр успешно сохранен: {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении сглаженного растра: {e}")


def visualize_raster(data, title="Raster", nodata_value=-9999):
    """
    Визуализация растра с исключением значений NoData.
    """
    valid_data = np.ma.masked_where(data == nodata_value, data)
    plt.figure(figsize=(10, 10))
    plt.imshow(valid_data, cmap="terrain", origin="upper")
    plt.colorbar(label="Height")
    plt.title(title)
    plt.show()


def process_las_files(las_folder, relief_output_folder, forest_output_folder, pixel_size=0.1, sigma=1.5):
    """
    Обработка всех .las файлов в папке: создание растров, сглаживание и сохранение.
    """
    try:
        # Создание выходных папок, если они не существуют
        os.makedirs(relief_output_folder, exist_ok=True)
        os.makedirs(forest_output_folder, exist_ok=True)

        # Поиск всех .las файлов в папке
        las_files = [f for f in os.listdir(las_folder) if f.endswith(".las")]
        if not las_files:
            print("В указанной папке нет .las файлов.")
            return

        for las_file in las_files:
            las_path = os.path.join(las_folder, las_file)
            print(f"Обработка файла: {las_path}")

            # Чтение данных из .las файла
            points = read_las_file(las_path)
            if points is None:
                continue

            # Определение типа файла: рельеф или лес
            base_name = os.path.splitext(las_file)[0]
            if "relief" in base_name.lower():
                output_folder = relief_output_folder
                is_relief = True
            elif "cloud" in base_name.lower():
                output_folder = forest_output_folder
                is_relief = False
            else:
                print(f"Неизвестный тип файла: {las_file}. Пропускаю.")
                continue

            # Создание имени выходного файла
            raster_output_path = os.path.join(output_folder, f"{base_name}_raster.tif")
            smoothed_output_path = os.path.join(output_folder, f"{base_name}_smoothed.tif")

            # Создание растра
            raster_data, bounds, _ = create_raster_from_points(points, raster_output_path, pixel_size=pixel_size)
            if raster_data is None:
                continue

            # Для рельефа: только сохраняем исходный растр
            if is_relief:
                print(f"Рельеф обработан и сохранен: {raster_output_path}")
                continue

            # Для леса: сглаживаем растр и сохраняем результат
            smoothed_data = smooth_raster(raster_data, sigma=sigma)

            # Визуализация исходного и сглаженного растра
            visualize_raster(raster_data, title="Original Raster")
            visualize_raster(smoothed_data, title="Smoothed Raster")

            # Сохранение сглаженного растра
            geo_transform = (
                bounds[0],  # x_min
                pixel_size,  # x_res
                0,
                bounds[3],  # y_max
                0,
                -pixel_size  # y_res
            )
            save_smoothed_raster(smoothed_data, geo_transform, smoothed_output_path)

    except Exception as e:
        print(f"Ошибка при обработке файлов: {e}")


if __name__ == "__main__":
    # Пути к папкам
    LAS_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud"
    RELIEF_OUTPUT_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF рельеф"
    FOREST_OUTPUT_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF лес"

    # Обработка всех .las файлов
    process_las_files(LAS_FOLDER, RELIEF_OUTPUT_FOLDER, FOREST_OUTPUT_FOLDER, pixel_size=0.1, sigma=1.5)