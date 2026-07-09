import itertools

def get_case_mutations(s):
    """Генерирует все возможные регистры для строки (н-р: a1 -> a1, A1)"""
    choices = [[c.lower(), c.upper()] if c.isalpha() else [c] for c in s]
    return ["".join(x) for x in itertools.product(*choices)]

def main():
    print("=== HUAWEI WPA2 KEYGEN ===")
    raw_mac = input("Введите MAC-адрес роутера: ").strip()
    
    mac = raw_mac.replace(":", "").replace("-", "").replace(".", "").lower()
    if len(mac) != 12:
        print("[-] Ошибка: MAC должен быть ровно 12 символов!")
        return

    candidates = set()
    print("[+] Запущена лютая чехарда паттернов... Подождите...")

    # Базовые куски MAC-адреса
    oui_6 = mac[:6]        # 18aa0f
    tail_6 = mac[6:]      # 5f3a3c
    tail_8 = mac[4:]      # 0f5f3a3c
    
    # 1. Все регистровые мутации чистого хвоста из 8 символов
    for mut in get_case_mutations(tail_8):
        candidates.add(mut)

    # 2. Перевороты байт хвоста (5f, 3a, 3c) + 2 ЛЮБЫХ знака (цифры и HEX-буквы)
    # Покрывает случаи: 3A3C5F??, ??3C5F3A, 3C??5F3A и т.д.
    tail_bytes = [tail_6[i:i+2] for i in range(0, 6, 2)]
    hex_pool = "0123456789abcdefABCDEF"
    
    for perm in itertools.permutations(tail_bytes):
        shuffled_tail = "".join(perm)
        # Добавляем 2 случайных HEX-символа во все возможные позиции (начало/конец)
        for p in itertools.product(hex_pool, repeat=2):
            pad = "".join(p)
            for m1 in get_case_mutations(pad + shuffled_tail): candidates.add(m1)
            for m2 in get_case_mutations(shuffled_tail + pad): candidates.add(m2)

    # 3. Жесткий сквозной брут: 4 буквы из MAC + 4 СЛУЧАЙНЫЕ ЦИФРЫ (смена мест)
    # Это создаст миллионы комбинаций, где буквы твоего роутера перемешаны с ЛЮБЫМИ цифрами
    mac_letters = list(set([c for c in mac if c.isalpha()]))
    # Если букв мало, добьем стандартными HEX-буквенными символами
    while len(mac_letters) < 4:
        mac_letters.extend(['a', 'b', 'c', 'd', 'e', 'f'])
    
    # Берем комбинации из 4 букв (в разных регистрах) и 4 любых цифр
    letter_variants = []
    for comb in itertools.combinations(mac_letters, 4):
        base = "".join(comb)
        for mut in get_case_mutations(base):
            letter_variants.append(list(mut))
            
    # Перебираем все цифровые хвосты от 0000 до 9999
    print("[+] Накатываем матрицы цифр от 0000 до 9999...")
    digital_blocks = [list(f"{i:04d}") for i in range(10000)]
    
    # Скрещиваем и делаем контролируемую чехарду позиций
    # Берем только первые 15000000 вариантов, чтобы скрипт не съел всю оперативку
    for lv in letter_variants[:100]:  # Ограничим базовые буквы для оптимизации памяти
        for db in digital_blocks:
            # Склеиваем: Буквы + Цифры, Цифры + Буквы, Чередование
            candidates.add("".join(lv + db))
            candidates.add("".join(db + lv))
            candidates.add("".join([lv[0], db[0], lv[1], db[1], lv[2], db[2], lv[3], db[3]]))
            candidates.add("".join([db[0], lv[0], db[1], lv[1], db[2], lv[2], db[3], lv[3]]))

    # 4. Паттерн «Инженерная соль» провайдеров
    # Подмешиваем частые префиксы к регистровому хвосту
    salts = ["hw", "hua", "gpon", "admin", "setup", "tl", "rt", "pd", "vld"]
    for salt in salts:
        rem_len = 8 - len(salt)
        if rem_len == 6:
            for m in get_case_mutations(salt + tail_6): candidates.add(m)
            for m in get_case_mutations(tail_6 + salt): candidates.add(m)
        elif rem_len == 4:
            tail_4 = tail_6[:4]
            for m in get_case_mutations(salt + tail_4): candidates.add(m)
            for m in get_case_mutations(tail_4 + salt): candidates.add(m)

    # Фильтруем строго по длине 8 символов
    print("[+] Фильтрация мусора...")
    final_list = [pwd for pwd in candidates if len(pwd) == 8]

    # Сохраняем огромную базу
    output_file = "huawei_chaos_dict.txt"
    print(f"[+] Записываем {len(final_list)} вариантов в файл...")
    with open(output_file, "w", encoding="utf-8") as f:
        for pwd in final_list:
            f.write(pwd + "\n")

    print(f"\n[+]Создан словарь: {output_file}")
    print(f"[+] Всего сгенерировано комбинаций: {len(final_list)}")
 


if __name__ == "__main__":
    main()
