import json
import os
from datetime import datetime

def analyze_challenges():
    file_path = 'data/tracker_backup.json'
    if not os.path.exists(file_path):
        print("[Ошибка]: Сначала сделай экспорт JSON из браузера в папку data/")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    archive = data.get('archive', [])
    if not archive:
        print("История квестов пуста. Иди выполняй задания!")
        return

    total_quests = len(archive)
    success_quests = [q for q in archive if q['status'] == 'success']
    failed_quests = [q for q in archive if q['status'] == 'fail']
    
    total_xp = sum(q['reward'] for q in success_quests)
    
    # Считаем самый популярный/частый проваленный квест
    fail_counts = {}
    for q in failed_quests:
        fail_counts[q['title']] = fail_counts.get(q['title'], 0) + 1
        
    most_failed = max(fail_counts, key=fail_counts.get) if fail_counts else "Нет провалов!"

    # Считаем среднее количество взятых квестов в активные дни
    unique_days = len(set(q['date'] for q in archive if 'date' in q))
    avg_per_day = total_quests / unique_days if unique_days > 0 else 0

    print("="*50)
    print("⚡ ОФФЛАЙН АНАЛИЗАТОР КВЕСТОВ И ЧЕЛЛЕНДЖЕЙ ⚡")
    print("="*50)
    print(f" Всего попыток: {total_quests}")
    print(f" Успешно закрыто квестов: {len(success_quests)} ✅")
    print(f" Слито заданий: {len(failed_quests)} 💀")
    print(f" Заработано опыта за всё время: {total_xp} XP 🏆")
    print(f" Самый сложный квест (чаще всего сливался): '{most_failed}'")
    print(f" Плотность безумия: {avg_per_day:.2f} квестов в активный день")
    print("="*50)

if __name__ == "__main__":
    analyze_challenges()
