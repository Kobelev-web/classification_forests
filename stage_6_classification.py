from config import *
from Efficintnet import classify_trees_and_update_shp

def stage_6():
    print("\nЭтап 6: Классификация деревьев...")
    classify_trees_and_update_shp(
        model_path=MODEL_PATH,
        image_folder=IMAGE_FOLDER,
        shp_path=SHP_PATH,
        output_shp_path=OUTPUT_SHP_PATH
    )
    print("Этап 6 завершен.")

if __name__ == "__main__":
    stage_6()