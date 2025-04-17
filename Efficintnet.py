import os
import torch
from torchvision import transforms
from PIL import Image
import geopandas as gpd
import timm
import sys
from collections import Counter

# Путь к модели и другим файлам
MODEL_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\model\efficientnet_b7.pth"
IMAGE_FOLDER = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Tree_profile"
SHP_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_height_las.shx"
OUTPUT_SHP_PATH = r"C:\Работа\Магистратура\Четвертый семестр\проект Таксация леса\Points\tree_crowns_with_class.shp"

# Словарь соответствия числовых классов и их названий
CLASS_MAPPING = {
    0: "ель",
    1: "береза",
    2: "сосна"
}

# Проверка существования файла модели
if not os.path.exists(MODEL_PATH):
    print(f"Ошибка: Файл модели {MODEL_PATH} не найден.")
    sys.exit(1)

def load_model(model_path):
    try:
        # Загрузка модели через timm
        model = timm.create_model('efficientnet_b7', pretrained=False)
        num_classes = len(CLASS_MAPPING)  # Укажите количество классов в вашей задаче
        model.classifier = torch.nn.Linear(model.classifier.in_features, num_classes)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        print("Модель успешно загружена.")
        return model
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        raise

# Предобработка изображения
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((600, 600)),  # Размер входного изображения для EfficientNet-B7
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)

# Классификация изображения
def classify_image(model, image_tensor):
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

# Основная функция
def classify_trees_and_update_shp(model_path, image_folder, shp_path, output_shp_path):
    # Загрузка модели
    model = load_model(model_path)

    # Загрузка SHP-файла
    crowns_gdf = gpd.read_file(shp_path)
    if 'tree_id' not in crowns_gdf.columns:
        raise ValueError("SHP-файл должен содержать атрибут 'tree_id'!")

    # Создание нового столбца для класса дерева
    crowns_gdf['tree_class'] = None

    # Обработка каждого дерева
    for idx, row in crowns_gdf.iterrows():
        tree_id = row['tree_id']

        # Проверка существования изображений с суффиксами _1 и _2
        image_names = [f"{tree_id}_1.png", f"{tree_id}_2.png"]
        classifications = []

        for image_name in image_names:
            image_path = os.path.join(image_folder, image_name)

            # Проверка существования изображения
            if not os.path.exists(image_path):
                print(f"Изображение {image_name} для дерева с ID {tree_id} не найдено. Пропускаем.")
                continue

            # Классификация изображения
            try:
                image_tensor = preprocess_image(image_path)
                tree_class = classify_image(model, image_tensor)
                classifications.append(tree_class)
                print(f"Дерево с ID {tree_id}, изображение {image_name} классифицировано как класс {tree_class}.")
            except Exception as e:
                print(f"Ошибка при классификации дерева с ID {tree_id}, изображение {image_name}: {e}")
                continue

        # Если есть хотя бы одна классификация, используем её
        if classifications:
            # Выбор наиболее часто встречающегося класса (или первого, если все разные)
            most_common_class = Counter(classifications).most_common(1)[0][0]
            # Преобразование числового класса в название
            class_name = CLASS_MAPPING.get(most_common_class, "неизвестный")
            crowns_gdf.at[idx, 'tree_class'] = class_name
        else:
            print(f"Для дерева с ID {tree_id} не найдено ни одного изображения.")

    # Сохранение обновленного SHP-файла
    crowns_gdf.to_file(output_shp_path, driver="ESRI Shapefile")
    print(f"Обновленный SHP-файл сохранен: {output_shp_path}")

# Проверка существования файла модели
if not os.path.exists(MODEL_PATH):
    print(f"Ошибка: Файл модели {MODEL_PATH} не найден.")
    sys.exit(1)

# Выполнение
if __name__ == "__main__":
    classify_trees_and_update_shp(MODEL_PATH, IMAGE_FOLDER, SHP_PATH, OUTPUT_SHP_PATH)