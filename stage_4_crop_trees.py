import os
from config import *
from crop import crop_point_cloud_by_polygons

def stage_4():
    print("\nЭтап 4: Вырезание отдельных деревьев...")
    crop_point_cloud_by_polygons(
        input_shp_path=input_shp_path,
        input_las_path=os.path.join(LAS_FOLDER, "Cloud.las"),
        output_folder=POINT_CLOUD_CROP_FOLDER
    )
    print("Этап 4 завершен.")

if __name__ == "__main__":
    stage_4()