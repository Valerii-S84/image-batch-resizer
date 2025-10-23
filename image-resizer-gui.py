#!/usr/bin/env python3
"""
Image Batch Resizer GUI
Графічний інтерфейс для зміни розміру зображень
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading


class ImageResizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Image Batch Resizer")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Змінні
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.mode = tk.StringVar(value='contain')
        self.bg_color = tk.StringVar(value='black')
        self.target_width = tk.IntVar(value=1280)
        self.target_height = tk.IntVar(value=720)
        
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Створення інтерфейсу"""
        # Заголовок
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header, 
            text="🖼️ IMAGE BATCH RESIZER",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Основний контейнер
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Секція 1: Вибір папки
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Папки", padding=15)
        folder_frame.pack(fill='x', pady=(0, 15))
        
        # Вхідна папка
        input_label = ttk.Label(folder_frame, text="Вхідна папка:")
        input_label.grid(row=0, column=0, sticky='w', pady=5)
        
        input_entry = ttk.Entry(folder_frame, textvariable=self.input_folder, width=50)
        input_entry.grid(row=0, column=1, padx=10, pady=5)
        
        input_btn = ttk.Button(folder_frame, text="Вибрати", command=self.select_input_folder)
        input_btn.grid(row=0, column=2, pady=5)
        
        # Вихідна папка
        output_label = ttk.Label(folder_frame, text="Вихідна папка:")
        output_label.grid(row=1, column=0, sticky='w', pady=5)
        
        output_entry = ttk.Entry(folder_frame, textvariable=self.output_folder, width=50)
        output_entry.grid(row=1, column=1, padx=10, pady=5)
        
        output_btn = ttk.Button(folder_frame, text="Вибрати", command=self.select_output_folder)
        output_btn.grid(row=1, column=2, pady=5)
        
        # Секція 2: Налаштування
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Налаштування", padding=15)
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Розмір
        size_label = ttk.Label(settings_frame, text="Цільовий розмір:")
        size_label.grid(row=0, column=0, sticky='w', pady=5)
        
        size_container = tk.Frame(settings_frame)
        size_container.grid(row=0, column=1, sticky='w', pady=5)
        
        width_entry = ttk.Entry(size_container, textvariable=self.target_width, width=8)
        width_entry.pack(side='left')
        
        x_label = ttk.Label(size_container, text=" x ")
        x_label.pack(side='left')
        
        height_entry = ttk.Entry(size_container, textvariable=self.target_height, width=8)
        height_entry.pack(side='left')
        
        # Режим
        mode_label = ttk.Label(settings_frame, text="Режим:")
        mode_label.grid(row=1, column=0, sticky='w', pady=5)
        
        mode_container = tk.Frame(settings_frame)
        mode_container.grid(row=1, column=1, sticky='w', pady=5)
        
        contain_radio = ttk.Radiobutton(
            mode_container, 
            text="Contain (з полями)", 
            variable=self.mode, 
            value='contain'
        )
        contain_radio.pack(side='left', padx=(0, 20))
        
        cover_radio = ttk.Radiobutton(
            mode_container, 
            text="Cover (без полів)", 
            variable=self.mode, 
            value='cover'
        )
        cover_radio.pack(side='left')
        
        # Колір фону
        color_label = ttk.Label(settings_frame, text="Колір фону:")
        color_label.grid(row=2, column=0, sticky='w', pady=5)
        
        color_combo = ttk.Combobox(
            settings_frame, 
            textvariable=self.bg_color,
            values=['black', 'white', 'gray'],
            state='readonly',
            width=15
        )
        color_combo.grid(row=2, column=1, sticky='w', pady=5)
        
        # Секція 3: Прогрес
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Прогрес", padding=15)
        progress_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill='x', pady=(0, 10))
        
        self.status_text = tk.Text(progress_frame, height=10, state='disabled')
        self.status_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        # Кнопка запуску
        self.start_btn = tk.Button(
            main_frame,
            text="🚀 ОБРОБИТИ ЗОБРАЖЕННЯ",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            height=2,
            command=self.start_processing
        )
        self.start_btn.pack(fill='x')
    
    def select_input_folder(self):
        """Вибір вхідної папки"""
        folder = filedialog.askdirectory(title="Виберіть папку з зображеннями")
        if folder:
            self.input_folder.set(folder)
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder, 'resized'))
    
    def select_output_folder(self):
        """Вибір вихідної папки"""
        folder = filedialog.askdirectory(title="Виберіть папку для збереження")
        if folder:
            self.output_folder.set(folder)
    
    def log(self, message):
        """Додати повідомлення в лог"""
        self.status_text.config(state='normal')
        self.status_text.insert('end', message + '\n')
        self.status_text.see('end')
        self.status_text.config(state='disabled')
        self.root.update()
    
    def resize_image(self, image_path, output_path):
        """Зміна розміру одного зображення"""
        try:
            img = Image.open(image_path)
            
            # Конвертуємо в RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            target_w = self.target_width.get()
            target_h = self.target_height.get()
            target_ratio = target_w / target_h
            img_ratio = img.width / img.height
            
            if self.mode.get() == 'contain':
                # Режим contain - зберігаємо все зображення
                if img_ratio > target_ratio:
                    new_width = target_w
                    new_height = int(target_w / img_ratio)
                else:
                    new_height = target_h
                    new_width = int(target_h * img_ratio)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Колір фону
                bg_colors = {
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'gray': (128, 128, 128)
                }
                bg = bg_colors.get(self.bg_color.get(), (0, 0, 0))
                
                new_img = Image.new('RGB', (target_w, target_h), bg)
                paste_x = (target_w - new_width) // 2
                paste_y = (target_h - new_height) // 2
                new_img.paste(img_resized, (paste_x, paste_y))
                
            else:
                # Режим cover - заповнюємо весь кадр
                if img_ratio > target_ratio:
                    new_height = target_h
                    new_width = int(target_h * img_ratio)
                else:
                    new_width = target_w
                    new_height = int(target_w / img_ratio)
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                left = (new_width - target_w) // 2
                top = (new_height - target_h) // 2
                new_img = img_resized.crop((left, top, left + target_w, top + target_h))
            
            # Зберігаємо
            new_img.save(output_path, 'JPEG', quality=95, optimize=True)
            return True
            
        except Exception as e:
            self.log(f"❌ Помилка: {e}")
            return False
    
    def process_images(self):
        """Обробка зображень"""
        input_dir = self.input_folder.get()
        output_dir = self.output_folder.get()
        
        if not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("Помилка", "Виберіть вхідну папку!")
            return
        
        # Створюємо вихідну папку
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Шукаємо зображення
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = [
            f for f in Path(input_dir).iterdir()
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        if not image_files:
            messagebox.showwarning("Увага", "Не знайдено зображень!")
            return
        
        self.log(f"📁 Знайдено {len(image_files)} зображень")
        self.log(f"🎯 Розмір: {self.target_width.get()}x{self.target_height.get()}")
        self.log(f"🔧 Режим: {self.mode.get()}")
        self.log("=" * 50)
        
        self.progress['maximum'] = len(image_files)
        success = 0
        
        for i, img_file in enumerate(image_files, 1):
            output_file = os.path.join(output_dir, f"{img_file.stem}_resized.jpg")
            
            self.log(f"[{i}/{len(image_files)}] {img_file.name}...")
            
            if self.resize_image(str(img_file), output_file):
                success += 1
                self.log("   ✅ Успішно")
            else:
                self.log("   ❌ Помилка")
            
            self.progress['value'] = i
            self.root.update()
        
        self.log("=" * 50)
        self.log(f"✅ Оброблено: {success}/{len(image_files)}")
        self.log(f"📂 Збережено в: {output_dir}")
        
        messagebox.showinfo("Готово", f"Оброблено {success} зображень!")
        
        self.start_btn.config(state='normal', text="🚀 ОБРОБИТИ ЗОБРАЖЕННЯ")
        self.processing = False
    
    def start_processing(self):
        """Запуск обробки"""
        if self.processing:
            return
        
        self.processing = True
        self.start_btn.config(state='disabled', text="⏳ Обробка...")
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', 'end')
        self.status_text.config(state='disabled')
        self.progress['value'] = 0
        
        # Запускаємо в окремому потоці
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    app = ImageResizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()