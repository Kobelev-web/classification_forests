from config import *
from tree_profile import add_las_attributes_and_plot

def stage_5():
    print("\nЭтап 5: Добавление атрибутов высоты из LAS-файлов и построение графиков...")
    add_las_attributes_and_plot(
        output_crowns_shp=output_crowns_shp,
        input_cropped_folder=input_cropped_folder,
        output_cropped_folder=output_cropped_folder,
        output_tree_profile_folder=output_tree_profile_folder
    )
    print("Этап 5 завершен.")

if __name__ == "__main__":
    stage_5()