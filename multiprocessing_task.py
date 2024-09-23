import os
import time
import multiprocessing

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

def worker_process(file_queue, keywords, result_queue):
    """
    Функція, яка виконується в кожному процесі.
    Обробляє файли з черги, шукаючи в них ключові слова.
    
    :param file_queue: Черга з файлами для обробки
    :param keywords: Список ключових слів для пошуку
    :param result_queue: Черга для збереження результатів пошуку
    """
    results = {}
    while True:
        try:
            file_path = file_queue.get_nowait()
        except:
            break
        file_results = search_file(file_path, keywords)
        for keyword, files in file_results.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(files)
    result_queue.put(results)

def multiprocess_search(file_list, keywords, num_processes):
    """
    Виконує багатопроцесорний пошук ключових слів у файлах.
    
    :param file_list: Список шляхів до файлів для обробки
    :param keywords: Список ключових слів для пошуку
    :param num_processes: Кількість процесів для використання
    :return: Словник результатів пошуку
    """
    manager = multiprocessing.Manager()
    file_queue = manager.Queue()
    result_queue = manager.Queue()

    # Заповнюємо чергу файлами
    for file_path in file_list:
        file_queue.put(file_path)

    # Створюємо та запускаємо процеси
    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=worker_process, args=(file_queue, keywords, result_queue))
        process.start()
        processes.append(process)

    # Очікуємо завершення всіх процесів
    for process in processes:
        process.join()

    # Збираємо результати з усіх процесів
    results = {}
    while not result_queue.empty():
        process_results = result_queue.get()
        for keyword, files in process_results.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(files)

    return results

def main():
    file_directory = "/Users/antonkorniyenko/VSCodeProjects/ComputerSystemsMSCbS/goit-cs-hw-04/test_files"  # Шлях до директорії з файлами
    file_list = [os.path.join(file_directory, f) for f in os.listdir(file_directory) if f.endswith('.txt')]
    keywords = ["python", "programming", "algorithm", "data"]
    num_processes = min(4, len(file_list))  # Використовуємо максимум 4 процеси або менше, якщо файлів менше

    print("Початок багатопроцесорного пошуку...")
    start_time = time.time()
    results = multiprocess_search(file_list, keywords, num_processes)
    end_time = time.time()
    
    execution_time_ms = (end_time - start_time) * 1000  # конвертуємо в мілісекунди
    print(f"Багатопроцесорний пошук завершено за {execution_time_ms:.2f} мілісекунд")
    
    print("Результати:")
    for keyword, files in results.items():
        print(f"'{keyword}': {files}")

    return results  # Повертаємо словник результатів

if __name__ == "__main__":
    main()
