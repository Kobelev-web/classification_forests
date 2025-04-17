from config import *
from rast import process_las_files

def stage_1():
    print("Этап 1: Создание растров из LAS-файлов...")
    process_las_files(
        las_folder=LAS_FOLDER,
        relief_output_folder=RELIEF_OUTPUT_FOLDER,
        forest_output_folder=FOREST_OUTPUT_FOLDER,
        pixel_size=PIXEL_SIZE,
        sigma=SIGMA
    )
    print("Этап 1 завершен.")

if __name__ == "__main__":
    stage_1()