from config import *
from tree_detection import find_tree_tops_with_coords

def stage_2():
    print("\nЭтап 2: Поиск вершин деревьев...")
    find_tree_tops_with_coords()
    print("Этап 2 завершен.")

if __name__ == "__main__":
    stage_2()