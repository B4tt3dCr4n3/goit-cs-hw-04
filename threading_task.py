import os
import time
import threading

def search_file(file_path, keywords):
    """
    Шукає ключові слова у заданому файлі.
    
    :param file_path: Шлях до файлу для пошуку
    :param keywords: Список ключових слів для пошуку
    :return: Словник, де ключі - це знайдені ключові слова, а значення - список файлів, де вони знайдені
    """
    results = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().lower()
            for keyword in keywords:
                if keyword.lower() in content:
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append(file_path)
    except Exception as e:
        print(f"Помилка при обробці файлу {file_path}: {str(e)}")
    return results

def worker_thread(file_list, keywords, results, lock):
    """
    Функція, яка виконується в кожному потоці.
    Обробляє файли зі свого списку, шукаючи в них ключові слова.
    
    :param file_list: Список файлів для обробки цим потоком
    :param keywords: Список ключових слів для пошуку
    :param results: Загальний словник результатів (спільний для всіх потоків)
    :param lock: Об'єкт блокування для безпечного оновлення results
    """
    thread_results = {}
    for file_path in file_list:
        file_results = search_file(file_path, keywords)
        # Оновлюємо локальний словник результатів потоку
        for keyword, files in file_results.items():
            if keyword not in thread_results:
                thread_results[keyword] = []
            thread_results[keyword].extend(files)
    
    # Оновлюємо загальний словник результатів
    with lock:
        for keyword, files in thread_results.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(files)

def threaded_search(file_list, keywords, num_threads):
    """
    Виконує багатопотоковий пошук ключових слів у файлах.
    
    :param file_list: Список шляхів до файлів для обробки
    :param keywords: Список ключових слів для пошуку
    :param num_threads: Кількість потоків для використання
    :return: Словник результатів пошуку
    """
    results = {}
    lock = threading.Lock()
    
    # Розділяємо список файлів на частини для кожного потоку
    files_per_thread = len(file_list) // num_threads
    thread_file_lists = [file_list[i:i + files_per_thread] for i in range(0, len(file_list), files_per_thread)]

    # Створюємо та запускаємо потоки
    threads = []
    for thread_files in thread_file_lists:
        thread = threading.Thread(target=worker_thread, args=(thread_files, keywords, results, lock))
        thread.start()
        threads.append(thread)

    # Очікуємо завершення всіх потоків
    for thread in threads:
        thread.join()

    return results

def main():
    file_directory = "/Users/antonkorniyenko/VSCodeProjects/ComputerSystemsMSCbS/goit-cs-hw-04/test_files"  # Шлях до директорії з файлами
    file_list = [os.path.join(file_directory, f) for f in os.listdir(file_directory) if f.endswith('.txt')]
    keywords = ["python", "programming", "algorithm", "data"]
    num_threads = min(4, len(file_list))  # Використовуємо максимум 4 потоки або менше, якщо файлів менше

    print("Початок багатопотокового пошуку...")
    start_time = time.time()
    results = threaded_search(file_list, keywords, num_threads)
    end_time = time.time()
    
    execution_time_ms = (end_time - start_time) * 1000  # конвертуємо в мілісекунди
    print(f"Багатопотоковий пошук завершено за {execution_time_ms:.2f} мілісекунд")
    
    print("Результати:")
    for keyword, files in results.items():
        print(f"'{keyword}': {files}")

    return results  # Повертаємо словник результатів

if __name__ == "__main__":
    main()
