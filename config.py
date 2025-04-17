# Пути к входным и выходным данным
LAS_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud"
RELIEF_OUTPUT_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF рельеф"
FOREST_OUTPUT_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF лес"
POINT_CLOUD_CROP_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud Crop"
TREE_PROFILE_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Tree_profile"

relief_raster_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF рельеф\relief_raster.tif"
trees_raster_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\GeoTIFF лес\Cloud_smoothed.tif"
output_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_tops.shp"
input_points_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_tops.shp"
output_polygons_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"
input_shp_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"
input_las_path = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud\Cloud.las"
output_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud Crop"
output_crowns_shp = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_attributes.shp"
input_cropped_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Point Cloud Crop"
output_cropped_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_height_las.shp"
output_tree_profile_folder = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Tree_profile"

# Модель классификации
MODEL_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\model\efficientnet_b7.pth"
IMAGE_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Tree_profile"
SHP_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_height_las.shx"
OUTPUT_SHP_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_class.shp"

# Параметры обработки
PIXEL_SIZE = 0.1  # Размер пикселя в метрах
SIGMA = 1.5       # Параметр сглаживания
MIN_DISTANCE_BETWEEN_TREES = 3  # Минимальное расстояние между деревьями (в пикселях)
k = 0.15  # Коэффициент для расчета диаметра кроны
CRS = "EPSG:32638"  # Система координат