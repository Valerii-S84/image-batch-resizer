#!/usr/bin/env python3
"""
Image Batch Resizer
Зменшує зображення до 1280x720 зі збереженням якості та пропорцій
"""

import os
from PIL import Image
from pathlib import Path
from typing import List, Tuple

class ImageResizer:
    def __init__(self, target_width=1280, target_height=720):
        """
        Ініціалізація ресайзера
        
        Args:
            target_width: Ширина вихідного зображення
            target_height: Висота вихідного зображення
        """
        self.target_width = target_width
        self.target_height = target_height
        self.target_ratio = target_width / target_height
        
    def resize_image_contain(self, image_path: str, output_path: str, 
                            bg_color=(0, 0, 0)) -> bool:
        """
        Зменшує зображення зі збереженням пропорцій (з padding)
        Вміщує все зображення, додаючи поля якщо потрібно
        
        Args:
            image_path: Шлях до вхідного зображення
            output_path: Шлях для збереження
            bg_color: Колір фону (чорний за замовчуванням)
        
        Returns:
            True якщо успішно, False якщо помилка
        """
        try:
            # Відкриваємо зображення
            img = Image.open(image_path)
            
            # Конвертуємо в RGB якщо потрібно
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, bg_color)
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Обчислюємо пропорції
            img_ratio = img.width / img.height
            
            # Визначаємо новий розмір зі збереженням пропорцій
            if img_ratio > self.target_ratio:
                # Зображення ширше ніж потрібно
                new_width = self.target_width
                new_height = int(self.target_width / img_ratio)
            else:
                # Зображення вище ніж потрібно
                new_height = self.target_height
                new_width = int(self.target_height * img_ratio)
            
            # Зменшуємо зображення з високою якістю
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Створюємо нове зображення з цільовим розміром
            new_img = Image.new('RGB', (self.target_width, self.target_height), bg_color)
            
            # Центруємо зменшене зображення
            paste_x = (self.target_width - new_width) // 2
            paste_y = (self.target_height - new_height) // 2
            new_img.paste(img_resized, (paste_x, paste_y))
            
            # Зберігаємо з високою якістю
            new_img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка при обробці {image_path}: {e}")
            return False
    
    def resize_image_cover(self, image_path: str, output_path: str) -> bool:
        """
        Зменшує зображення заповнюючи весь кадр (може обрізати краї)
        
        Args:
            image_path: Шлях до вхідного зображення
            output_path: Шлях для збереження
        
        Returns:
            True якщо успішно, False якщо помилка
        """
        try:
            img = Image.open(image_path)
            
            # Конвертуємо в RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Обчислюємо пропорції
            img_ratio = img.width / img.height
            
            # Масштабуємо щоб заповнити весь кадр
            if img_ratio > self.target_ratio:
                # Зображення ширше - масштабуємо по висоті
                new_height = self.target_height
                new_width = int(self.target_height * img_ratio)
            else:
                # Зображення вище - масштабуємо по ширині
                new_width = self.target_width
                new_height = int(self.target_width / img_ratio)
            
            # Зменшуємо
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Обрізаємо до потрібного розміру (центруємо)
            left = (new_width - self.target_width) // 2
            top = (new_height - self.target_height) // 2
            right = left + self.target_width
            bottom = top + self.target_height
            
            img_cropped = img_resized.crop((left, top, right, bottom))
            
            # Зберігаємо
            img_cropped.save(output_path, 'JPEG', quality=95, optimize=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка при обробці {image_path}: {e}")
            return False
    
    def process_folder(self, input_folder: str, output_folder: str = None, 
                      mode: str = 'contain', bg_color=(0, 0, 0)) -> Tuple[int, int]:
        """
        Обробляє всі зображення в папці
        
        Args:
            input_folder: Папка з вхідними зображеннями
            output_folder: Папка для збереження (створюється автоматично)
            mode: 'contain' (з полями) або 'cover' (без полів)
            bg_color: Колір фону для режиму contain
        
        Returns:
            (кількість успішних, кількість помилок)
        """
        # Створюємо output папку
        if output_folder is None:
            output_folder = os.path.join(input_folder, 'resized')
        
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # Підтримувані формати
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        # Шукаємо зображення
        input_path = Path(input_folder)
        image_files = [
            f for f in input_path.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        if not image_files:
            print("❌ Не знайдено зображень для обробки!")
            return 0, 0
        
        print(f"📁 Знайдено {len(image_files)} зображень")
        print(f"🎯 Цільовий розмір: {self.target_width}x{self.target_height}")
        print(f"🔧 Режим: {mode}")
        print(f"💾 Зберігаємо в: {output_folder}")
        print("-" * 50)
        
        success_count = 0
        error_count = 0
        
        # Обробляємо кожне зображення
        for i, image_file in enumerate(image_files, 1):
            output_file = os.path.join(output_folder, f"{image_file.stem}_resized.jpg")
            
            print(f"[{i}/{len(image_files)}] Обробка: {image_file.name}...", end=' ')
            
            if mode == 'contain':
                success = self.resize_image_contain(str(image_file), output_file, bg_color)
            else:
                success = self.resize_image_cover(str(image_file), output_file)
            
            if success:
                success_count += 1
                print("✅")
            else:
                error_count += 1
                print("❌")
        
        print("-" * 50)
        print(f"✅ Успішно оброблено: {success_count}")
        if error_count > 0:
            print(f"❌ Помилок: {error_count}")
        print(f"📂 Результат збережено в: {output_folder}")
        
        return success_count, error_count


def main():
    """Головна функція"""
    print("=" * 60)
    print("🖼️  IMAGE BATCH RESIZER")
    print("=" * 60)
    print()
    
    # Налаштування
    print("⚙️  Налаштування:")
    print("   Цільовий розмір: 1280 x 720")
    print()
    
    # Запитуємо шлях до папки
    input_folder = input("📁 Вкажіть шлях до папки з зображеннями: ").strip()
    
    if not os.path.exists(input_folder):
        print("❌ Папка не знайдена!")
        return
    
    # Вибір режиму
    print()
    print("🔧 Виберіть режим:")
    print("   1. CONTAIN - Зберігає все зображення, додає чорні поля якщо потрібно (рекомендовано)")
    print("   2. COVER - Заповнює весь кадр, може обрізати краї")
    
    mode_choice = input("Ваш вибір (1 або 2): ").strip()
    mode = 'contain' if mode_choice != '2' else 'cover'
    
    # Колір фону для contain режиму
    bg_color = (0, 0, 0)  # Чорний за замовчуванням
    if mode == 'contain':
        print()
        print("🎨 Виберіть колір фону (для полів):")
        print("   1. Чорний (рекомендовано)")
        print("   2. Білий")
        print("   3. Сірий")
        color_choice = input("Ваш вибір (1, 2 або 3): ").strip()
        
        if color_choice == '2':
            bg_color = (255, 255, 255)
        elif color_choice == '3':
            bg_color = (128, 128, 128)
    
    print()
    print("🚀 Початок обробки...")
    print()
    
    # Створюємо resizer та обробляємо
    resizer = ImageResizer(1280, 720)
    success, errors = resizer.process_folder(input_folder, mode=mode, bg_color=bg_color)
    
    print()
    print("=" * 60)
    print("🎉 ЗАВЕРШЕНО!")
    print("=" * 60)
    
    input("\nНатисніть Enter для виходу...")


if __name__ == "__main__":
    main()