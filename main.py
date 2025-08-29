import numpy as np
import matplotlib.pyplot as plt
import random

# === Параметры по умолчанию ===
A = 1.0       # Амплитуда
f0 = 1000.0   # Базовая частота (несущая)
Tb = 1.0      # Длительность бита
h = 0.5       # Индекс модуляции
bits = []     # Битовая последовательность
seq_len = 8   # Длина последовательности по умолчанию

# === Справка по командам ===
def print_help():
    print("\nДоступные команды:")
    print("  change A <value>      - изменить амплитуду сигнала")
    print("  change f0 <value>     - изменить базовую частоту (несущую)")
    print("  change Tb <value>     - изменить длительность бита")
    print("  change h <value>      - изменить индекс модуляции")
    print("  set bits <sequence>   - установить битовую последовательность (0 и 1)")
    print("  run                   - выполнить расчёт и построить график")
    print("  help                  - показать этот список команд")
    print("  exit                  - выход из программы\n")

# === Ввод длины последовательности ===
while True:
    inp = input("Введите длину последовательности (4, 8, 16, 24) или оставьте пустым для 8: ").strip()
    if inp == "":
        seq_len = 8
        break
    elif inp.isdigit() and int(inp) in [4,8,16,24]:
        seq_len = int(inp)
        break
    else:
        print("❌ Некорректная длина, попробуйте снова.")

print("\nВведите команду. Для списка команд введите 'help'. Чтобы завершить — 'exit'.\n")

# === Основной цикл команд ===
while True:
    cmd = input("> ").strip()
    if not cmd:
        continue
    parts = cmd.split()
    cmd_lower = parts[0].lower()
    
    if cmd_lower == "help":
        print_help()
    
    elif cmd_lower == "exit":
        print("Выход...")
        break
    
    elif cmd_lower == "change" and len(parts) == 3:
        param, val = parts[1], parts[2]
        try:
            val_num = float(val)
            if param == "A":
                if val_num <= 0:
                    raise ValueError
                A = val_num
            elif param == "f0":
                f0 = val_num
            elif param == "Tb":
                if val_num <= 0:
                    raise ValueError
                Tb = val_num
            elif param == "h":
                h = val_num
            else:
                print("❌ Неизвестный параметр:", param)
                continue
            print(f"✅ {param} изменён на {val_num}")
        except:
            print("❌ Ошибка: значение должно быть корректным числом >0 для A и Tb (h может быть любое число)")

    elif cmd_lower == "set" and len(parts) == 3 and parts[1].lower() == "bits":
        seq = parts[2]
        if len(seq) == seq_len and set(seq) <= {"0","1"}:
            bits = [int(b) for b in seq]
            print(f"✅ Последовательность установлена: {seq}")
        else:
            print(f"❌ Ошибка: последовательность должна быть длиной {seq_len} и содержать только 0 и 1")
    
    elif cmd_lower == "run":
        if not bits:
            bits = [random.choice([0,1]) for _ in range(seq_len)]
            print("Сгенерирована случайная последовательность:", "".join(map(str, bits)))

        # === Расчёт формул и сигналов ===
        phi_exprs = []
        freq_exprs = []
        integral_exprs = []
        piecewise_exprs = []
        phi_val = 0

        for i, b in enumerate(bits):
            m = 1 if b == 1 else -1
            f_inst = f0 + (h/Tb)*m
            integral_formula = f"∫ {f_inst} dτ = {f_inst}·(t-{i*Tb})"
            phi_formula = f"{phi_val:.2f} + 2π·{f_inst}·(t-{i*Tb}),  t∈[{i*Tb}, {(i+1)*Tb})"
            freq_formula = f"f_inst(t) = {f_inst} Гц,  t∈[{i*Tb}, {(i+1)*Tb})"
            piecewise_exprs.append(f"s(t) = {A}·cos({phi_formula})")
            integral_exprs.append(integral_formula)
            phi_exprs.append(phi_formula)
            freq_exprs.append(freq_formula)
            phi_val += 2*np.pi*f_inst*Tb

        # === Запись в файл ===
        with open("results.txt", "w", encoding="utf-8") as f:
            f.write("=== CPFSK АНАЛИЗ ===\n\n")
            f.write("Битовая последовательность: " + "".join(map(str, bits)) + "\n\n")
            f.write("1. Интегралы:\n")
            for line in integral_exprs:
                f.write("  "+line+"\n")
            f.write("\n2. Фаза:\n")
            for line in phi_exprs:
                f.write("  "+line+"\n")
            f.write("\n3. Мгновенная частота:\n")
            for line in freq_exprs:
                f.write("  "+line+"\n")
            f.write("\n4. Итоговая кусочная формула сигнала:\n")
            for line in piecewise_exprs:
                f.write("  "+line+"\n")
        print("✅ Формулы и результаты сохранены в results.txt")

        # === Построение графика без интерактивных окон ===
        time = np.linspace(0, len(bits)*Tb, 1000)
        signal = np.zeros_like(time)
        phi_val = 0
        for i, b in enumerate(bits):
            m = 1 if b == 1 else -1
            f_inst = f0 + (h/Tb)*m
            idx = (time >= i*Tb) & (time < (i+1)*Tb)
            t_interval = time[idx]
            phi_segment = phi_val + 2*np.pi*f_inst*(t_interval - i*Tb)
            signal[idx] = A * np.cos(phi_segment)
            phi_val = phi_segment[-1]

        plt.figure(figsize=(10,4))
        plt.plot(time, signal, label=f"CPFSK сигнал (A={A}, f0={f0}, Tb={Tb}, h={h})")
        plt.xlabel("Время")
        plt.ylabel("Амплитуда")
        plt.title("CPFSK сигнал")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig("cpfsksignal.png", dpi=150)
        plt.close()
        print("✅ График сохранён в cpfsksignal.png (без открытия окон)")

    else:
        print("❌ Неизвестная команда. Введите 'help' для списка команд")
