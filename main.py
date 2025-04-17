from stage_1_raster_creation import stage_1
from stage_2_tree_detection import stage_2
from stage_3_crown_polygons import stage_3
from stage_4_crop_trees import stage_4
from stage_5_add_attributes import stage_5
from stage_6_classification import stage_6

def main():
    print("Начало обработки проекта таксации леса...")

    # Выполнение этапов
    stage_1()
    stage_2()
    stage_3()
    stage_4()
    stage_5()
    stage_6()

    print("\nОбработка завершена!")

if __name__ == "__main__":
    main()