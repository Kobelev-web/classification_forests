from config import *
from crona import create_crown_polygons_with_attributes
from config import k


def stage_3():
    print("\nЭтап 3: Создание полигонов крон деревьев...")
    create_crown_polygons_with_attributes(
        input_points_path=input_points_path,
        output_polygons_path=output_polygons_path,
        k=k
    )
    print("Этап 3 завершен.")

if __name__ == "__main__":
    stage_3()