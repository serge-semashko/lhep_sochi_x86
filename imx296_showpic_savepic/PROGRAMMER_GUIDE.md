# Programmer Guide - IMX296 Camera Viewer and Capture

Техническое руководство для разработчиков по работе с проектом IMX296 Camera Viewer and Capture.

## Содержание

1. [Архитектура системы](#архитектура-системы)
2. [Детальный разбор кода](#детальный-разбор-кода)
3. [API и интерфейсы](#api-и-интерфейсы)
4. [Потоки данных](#потоки-данных)
5. [Обработка ошибок](#обработка-ошибок)
6. [Производительность и оптимизация](#производительность-и-оптимизация)
7. [Расширение функциональности](#расширение-функциональности)
8. [Отладка и диагностика](#отладка-и-диагностика)

---

## Архитектура системы

### Общая структура

Проект представляет собой однопоточное приложение для захвата и обработки изображений с камеры IMX296 на Raspberry Pi. Архитектура следует паттерну последовательной обработки данных:

```
[Камера IMX296] → [Picamera2 API] → [Обработка кадра] → [Отображение] → [Сохранение]
                                                      ↓
                                              [Пользовательский ввод]
```

### Компоненты системы

1. **Модуль инициализации** (`s296.py`, строки 1-13)
   - Загрузка зависимостей
   - Инициализация переменных окружения

2. **Модуль работы с камерой** (`live_camera_view()`, строки 14-63)
   - Конфигурация камеры
   - Захват кадров
   - Обработка изображений

3. **Модуль сохранения** (встроен в основной цикл)
   - Генерация имен файлов
   - Управление файловой системой
   - Запись изображений

### Зависимости и библиотеки

| Библиотека | Версия | Назначение | Критичность |
|------------|--------|------------|-------------|
| `picamera2` | - | Работа с камерой Raspberry Pi | Критично |
| `opencv-python` (cv2) | - | Обработка и отображение изображений | Критично |
| `python-dotenv` | - | Загрузка переменных окружения | Опционально |
| `time` | stdlib | Работа со временем | Критично |
| `os` | stdlib | Файловая система | Критично |
| `pathlib` | stdlib | Работа с путями | Критично |

---

## Детальный разбор кода

### Модуль s296.py

#### Импорты и инициализация (строки 1-13)

```python
import cv2
from picamera2 import Picamera2
import time
from os import environ
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print(' python-dotenv not installed, rely on environment variable')
```

**Анализ:**

- **Строки 1-6**: Стандартные импорты без обработки ошибок - библиотеки должны быть установлены
- **Строки 7-12**: Опциональная загрузка `.env` файла
  - Использует `Path(__file__).parent` для определения корневой директории проекта
  - Обрабатывает `ImportError` gracefully - программа продолжит работу без dotenv
  - Потенциальная проблема: если `.env` существует, но dotenv не установлен, файл будет проигнорирован без предупреждения

**Рекомендации по улучшению:**

```python
# Добавить проверку существования .env файла
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file)
    except ImportError:
        print('Warning: .env file found but python-dotenv not installed')
```

#### Функция live_camera_view() - Инициализация (строки 14-30)

```python
def live_camera_view():
    # Create a Picamera2 object
    picam2 = Picamera2()
    
    # Set up video configuration
    print(environ.get("GAIN"), environ.get("EXPOSURE_TIME"))
    picam2_gain = float(environ.get("GAIN"))
    picam2_ExposureTime = int(environ.get("EXPOSURE_TIME"))
    
    config = picam2.create_video_configuration()
    controls = {'ExposureTime': picam2_ExposureTime, 'AnalogueGain': picam2_gain, 'FrameRate': 40}
    config = picam2.create_still_configuration(controls=controls)
    
    picam2.configure(config)
    picam2.start()
```

**Детальный анализ:**

1. **Создание объекта камеры (строка 16)**
   - `Picamera2()` создает объект для работы с камерой
   - Не требует параметров - автоматически определяет доступную камеру
   - Может вызвать исключение, если камера не найдена

2. **Чтение параметров (строки 19-21)**
   - **Проблема**: Нет проверки на `None` - если переменные не установлены, `float(None)` и `int(None)` вызовут `TypeError`
   - **Проблема**: Нет валидации диапазонов значений
   - Вывод в консоль происходит до преобразования типов

3. **Конфигурация камеры (строки 23-25)**
   - **Интересная особенность**: Сначала создается `video_configuration`, но не используется
   - Затем создается `still_configuration` с теми же controls
   - Это позволяет использовать параметры экспозиции из режима фотографии при непрерывном захвате
   - `FrameRate: 40` жестко задан в коде

4. **Применение конфигурации (строки 27-30)**
   - `configure()` применяет настройки
   - `start()` инициализирует захват кадров

**Улучшенная версия:**

```python
def live_camera_view():
    picam2 = Picamera2()
    
    # Безопасное чтение параметров с валидацией
    gain_str = environ.get("GAIN")
    exposure_str = environ.get("EXPOSURE_TIME")
    
    if gain_str is None or exposure_str is None:
        raise ValueError("GAIN and EXPOSURE_TIME must be set as environment variables")
    
    try:
        picam2_gain = float(gain_str)
        picam2_ExposureTime = int(exposure_str)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid parameter format: {e}")
    
    # Валидация диапазонов
    if not (1.0 <= picam2_gain <= 64.0):
        raise ValueError(f"GAIN must be between 1.0 and 64.0, got {picam2_gain}")
    if picam2_ExposureTime <= 0:
        raise ValueError(f"EXPOSURE_TIME must be positive, got {picam2_ExposureTime}")
    
    print(f"Camera settings: GAIN={picam2_gain}, EXPOSURE_TIME={picam2_ExposureTime}")
    
    # Конфигурация
    controls = {
        'ExposureTime': picam2_ExposureTime,
        'AnalogueGain': picam2_gain,
        'FrameRate': 40
    }
    config = picam2.create_still_configuration(controls=controls)
    picam2.configure(config)
    picam2.start()
```

#### Основной цикл захвата (строки 34-54)

```python
try:
    while True:
        # Capture an image (in numpy array format)
        frame = picam2.capture_array()
        
        # Convert the image to BGR format (the format used by OpenCV)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Display the image on the screen
        cv2.imshow('Live Camera Feed', frame_bgr)
        tm = time.gmtime()
        if not os.path.exists('images'):
            os.makedirs('images')    
        file_name ='images/'+ str(tm.tm_mon) + '-' + str(tm.tm_mday) + '_' + str(tm.tm_hour) + '-' + str(tm.tm_min) + '-'+str(tm.tm_sec) + '.png'
        
        cv2.imwrite(file_name, frame)
        
        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
```

**Детальный анализ:**

1. **Захват кадра (строка 37)**
   - `capture_array()` возвращает numpy array в формате RGB
   - Блокирующий вызов - программа ждет готовности кадра
   - Формат данных: `numpy.ndarray` с shape `(height, width, 3)` для цветного изображения

2. **Конвертация цветового пространства (строка 40)**
   - OpenCV использует BGR вместо RGB
   - `cv2.cvtColor()` выполняет преобразование
   - Создается копия массива - дополнительное использование памяти

3. **Отображение (строка 43)**
   - `cv2.imshow()` обновляет окно (или создает, если не существует)
   - Неблокирующий вызов
   - Требует последующего `cv2.waitKey()` для обработки событий окна

4. **Генерация имени файла (строки 44-47)**
   - **Проблема**: Проверка существования папки происходит на каждой итерации цикла
   - **Проблема**: Форматирование строки не использует форматирование Python (f-strings или format)
   - **Проблема**: Возможны коллизии имен файлов при высокой частоте кадров (40 fps)
   - Используется UTC время (`time.gmtime()`)

5. **Сохранение изображения (строка 49)**
   - Сохраняется оригинальный RGB кадр, а не BGR версия для отображения
   - PNG формат без сжатия - большие файлы
   - Блокирующая операция I/O

6. **Обработка ввода (строка 53)**
   - `cv2.waitKey(1)` проверяет нажатия клавиш с таймаутом 1 мс
   - `& 0xFF` извлекает младший байт (для совместимости)
   - Проверка на 'q' для выхода

**Улучшенная версия:**

```python
try:
    # Создать папку один раз перед циклом
    images_dir = Path('images')
    images_dir.mkdir(exist_ok=True)
    
    frame_count = 0
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('Live Camera Feed', frame_bgr)
        
        # Генерация уникального имени файла
        tm = time.gmtime()
        file_name = images_dir / f"{tm.tm_mon:02d}-{tm.tm_mday:02d}_{tm.tm_hour:02d}-{tm.tm_min:02d}-{tm.tm_sec:02d}_{frame_count:04d}.png"
        cv2.imwrite(str(file_name), frame)
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
```

#### Обработка ошибок (строки 56-63)

```python
except KeyboardInterrupt:
    # When the user wants to exit with Ctrl+C
    print("\nProgram is terminating...")

finally:
    # Stop the camera and close OpenCV windows
    picam2.stop()
    cv2.destroyAllWindows()
```

**Анализ:**

- **Хорошо**: Используется `finally` для гарантированного освобождения ресурсов
- **Проблема**: `KeyboardInterrupt` обрабатывается только для Ctrl+C, но не для других исключений
- **Проблема**: Нет обработки ошибок камеры (например, потеря соединения)
- **Проблема**: Нет логирования ошибок

**Улучшенная версия:**

```python
except KeyboardInterrupt:
    print("\nProgram is terminating...")
except Exception as e:
    print(f"\nError occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        picam2.stop()
    except Exception as e:
        print(f"Error stopping camera: {e}")
    cv2.destroyAllWindows()
```

---

## API и интерфейсы

### Внешний API

#### Переменные окружения

| Переменная | Тип | Диапазон | Обязательность | Описание |
|------------|-----|----------|----------------|----------|
| `GAIN` | float | 1.0 - 64.0 | Да | Аналоговое усиление камеры |
| `EXPOSURE_TIME` | int | > 0 | Да | Время экспозиции в микросекундах |

#### Файловая система

**Вход:**
- `.env` (опционально) - файл с переменными окружения

**Выход:**
- `images/` - директория с сохраненными изображениями
- Формат имени: `MM-DD_HH-MM-SS.png` (UTC время)

### Внутренний API

#### Функция `live_camera_view()`

**Сигнатура:**
```python
def live_camera_view() -> None
```

**Параметры:** Нет

**Возвращаемое значение:** `None`

**Побочные эффекты:**
- Создает окно OpenCV "Live Camera Feed"
- Создает директорию `images/` если не существует
- Сохраняет изображения на диск
- Выводит сообщения в консоль

**Исключения:**
- `TypeError` - если переменные окружения не установлены
- `ValueError` - если параметры имеют неверный формат
- `RuntimeError` - если камера недоступна
- `KeyboardInterrupt` - при нажатии Ctrl+C

---

## Потоки данных

### Поток обработки кадра

```
[Камера IMX296]
    ↓ (через драйвер Linux)
[Picamera2 API]
    ↓ capture_array() → numpy.ndarray (RGB, uint8)
[Обработка в памяти]
    ↓ cvtColor(RGB→BGR) → numpy.ndarray (BGR, uint8)
[Отображение]
    ↓ imshow() → OpenCV Window
[Пользователь видит кадр]
    ↓
[Параллельно: Сохранение]
    ↓ imwrite() → PNG файл на диск
[Файловая система]
```

### Форматы данных

#### Входной формат (от камеры)
- **Тип**: `numpy.ndarray`
- **Dtype**: `numpy.uint8`
- **Shape**: `(height, width, 3)` для цветного изображения
- **Цветовое пространство**: RGB
- **Разрешение**: Зависит от конфигурации камеры

#### Промежуточный формат (для отображения)
- **Тип**: `numpy.ndarray`
- **Dtype**: `numpy.uint8`
- **Shape**: `(height, width, 3)`
- **Цветовое пространство**: BGR (для OpenCV)

#### Выходной формат (на диск)
- **Формат файла**: PNG
- **Цветовое пространство**: RGB (оригинальное)
- **Сжатие**: Нет (без потерь)
- **Размер файла**: Зависит от разрешения (примерно 3-10 МБ на кадр для высокого разрешения)

### Поток управления

```
[Запуск программы]
    ↓
[Инициализация переменных окружения]
    ↓
[Создание объекта Picamera2]
    ↓
[Конфигурация камеры]
    ↓
[Запуск камеры]
    ↓
[Основной цикл: захват → обработка → отображение → сохранение]
    ↓ (пока не нажата 'q' или Ctrl+C)
[Остановка камеры]
    ↓
[Закрытие окон]
    ↓
[Завершение программы]
```

---

## Обработка ошибок

### Текущая реализация

Программа обрабатывает только `KeyboardInterrupt` (Ctrl+C). Все остальные исключения приведут к аварийному завершению.

### Потенциальные проблемы

1. **Отсутствие переменных окружения**
   - Симптом: `TypeError: float() argument must be a string or a real number, not 'NoneType'`
   - Место: строка 20-21
   - Решение: Добавить проверку перед преобразованием типов

2. **Камера недоступна**
   - Симптом: `RuntimeError` при создании `Picamera2()` или `start()`
   - Место: строки 16, 30
   - Решение: Обработать исключение с понятным сообщением

3. **Недостаточно места на диске**
   - Симптом: `OSError` при `cv2.imwrite()`
   - Место: строка 49
   - Решение: Проверять свободное место или обрабатывать исключение

4. **Нет прав на запись**
   - Симптом: `PermissionError` при создании папки или записи файла
   - Место: строки 45-46, 49
   - Решение: Проверять права доступа

5. **Коллизии имен файлов**
   - Симптом: Перезапись файлов при высокой частоте кадров
   - Место: строка 47
   - Решение: Добавить счетчик кадров или микросекунды в имя файла

### Рекомендации по улучшению

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def live_camera_view():
    try:
        # ... инициализация ...
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Camera error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
```

---

## Производительность и оптимизация

### Текущие характеристики

- **Частота захвата**: До 40 fps (ограничено `FrameRate`)
- **Задержка отображения**: ~25-50 мс (зависит от разрешения)
- **Использование CPU**: Высокое (однопоточная обработка)
- **Использование памяти**: Среднее (зависит от разрешения камеры)

### Узкие места производительности

1. **Сохранение каждого кадра на диск**
   - Операция I/O блокирующая
   - PNG без сжатия - большие файлы
   - Решение: Использовать отдельный поток для сохранения или очередь

2. **Проверка существования папки на каждой итерации**
   - Лишние системные вызовы
   - Решение: Проверять один раз перед циклом

3. **Конвертация RGB→BGR для каждого кадра**
   - Дополнительное использование памяти
   - Решение: Использовать нативные форматы или оптимизировать конвертацию

4. **Синхронный захват кадров**
   - Блокирующий вызов `capture_array()`
   - Решение: Использовать асинхронный захват или буферизацию

### Рекомендации по оптимизации

#### 1. Асинхронное сохранение

```python
from queue import Queue
from threading import Thread

def save_worker(queue):
    while True:
        frame, filename = queue.get()
        if frame is None:  # Сигнал завершения
            break
        cv2.imwrite(filename, frame)
        queue.task_done()

save_queue = Queue(maxsize=100)
save_thread = Thread(target=save_worker, args=(save_queue,))
save_thread.start()

# В основном цикле:
save_queue.put((frame, file_name))
```

#### 2. Оптимизация конвертации цветов

```python
# Использовать numpy slicing вместо cvtColor (быстрее для некоторых случаев)
frame_bgr = frame[:, :, ::-1]  # Инвертировать последнюю ось (RGB→BGR)
```

#### 3. Условное сохранение

```python
SAVE_EVERY_N_FRAMES = 5  # Сохранять каждый 5-й кадр
frame_count = 0

while True:
    frame = picam2.capture_array()
    # ... обработка ...
    
    if frame_count % SAVE_EVERY_N_FRAMES == 0:
        cv2.imwrite(file_name, frame)
    frame_count += 1
```

---

## Расширение функциональности

### Возможные улучшения

#### 1. Добавление параметров командной строки

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='IMX296 Camera Viewer')
    parser.add_argument('--gain', type=float, default=None,
                       help='Camera gain (1.0-64.0)')
    parser.add_argument('--exposure', type=int, default=None,
                       help='Exposure time in microseconds')
    parser.add_argument('--fps', type=int, default=40,
                       help='Frame rate')
    parser.add_argument('--output-dir', type=str, default='images',
                       help='Output directory for images')
    parser.add_argument('--save-every', type=int, default=1,
                       help='Save every N frames')
    return parser.parse_args()
```

#### 2. Поддержка различных форматов сохранения

```python
def save_frame(frame, filename, format='png'):
    if format == 'png':
        cv2.imwrite(filename, frame)
    elif format == 'jpg':
        cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    elif format == 'raw':
        frame.tofile(filename)
```

#### 3. Добавление метаданных в EXIF

```python
from PIL import Image
from PIL.ExifTags import TAGS

def add_exif_metadata(image_path, gain, exposure_time):
    img = Image.open(image_path)
    exif = img.getexif()
    # Добавить метаданные
    # ...
```

#### 4. Режим записи видео

```python
import cv2

def record_video(output_file='output.avi', duration=60):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 40.0, (width, height))
    
    start_time = time.time()
    while time.time() - start_time < duration:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    
    out.release()
```

#### 5. Веб-интерфейс для удаленного управления

```python
from flask import Flask, render_template, Response

app = Flask(__name__)

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')
```

---

## Отладка и диагностика

### Инструменты отладки

#### 1. Логирование

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('camera.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Профилирование производительности

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... код программы ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Топ-20 функций по времени выполнения
```

#### 3. Измерение FPS

```python
import time

fps_counter = []
while True:
    start = time.time()
    frame = picam2.capture_array()
    # ... обработка ...
    elapsed = time.time() - start
    fps_counter.append(1.0 / elapsed if elapsed > 0 else 0)
    
    if len(fps_counter) > 100:
        avg_fps = sum(fps_counter[-100:]) / 100
        print(f"Average FPS: {avg_fps:.2f}")
```

#### 4. Мониторинг памяти

```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
```

### Типичные проблемы и решения

#### Проблема: Низкая частота кадров

**Диагностика:**
```python
import time
start = time.time()
frame = picam2.capture_array()
print(f"Capture time: {(time.time() - start) * 1000:.2f} ms")
```

**Решения:**
- Уменьшить разрешение камеры
- Оптимизировать обработку кадров
- Использовать более быстрый диск для сохранения

#### Проблема: Высокое использование памяти

**Диагностика:**
```python
import sys
frame = picam2.capture_array()
print(f"Frame size: {sys.getsizeof(frame) / 1024 / 1024:.2f} MB")
```

**Решения:**
- Очищать неиспользуемые переменные
- Использовать генераторы вместо списков
- Ограничить размер буферов

#### Проблема: Потеря кадров

**Диагностика:**
- Добавить счетчик кадров
- Сравнить ожидаемое и фактическое количество сохраненных файлов

**Решения:**
- Использовать асинхронное сохранение
- Увеличить размер очереди
- Оптимизировать операции I/O

---

## Заключение

Данное руководство предоставляет полное техническое описание программы `s296.py` для работы с камерой IMX296. При разработке расширений или исправлении ошибок рекомендуется следовать описанным здесь паттернам и рекомендациям.

Для получения дополнительной информации см.:
- [README.md](README.md) - Общее описание проекта
- [Документация Picamera2](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Документация OpenCV](https://docs.opencv.org/)

