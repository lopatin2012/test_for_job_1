import csv
import json
import datetime
import re


def warning(file_path: str, index: int, row: str, message: str):
    # Функция для предупреждений и записи в лог-файл ошибок по ValueError.
    log_file_name = datetime.datetime.now().strftime("%d.%m.%Y")
    with open(f"log_{file_path}_{log_file_name}.txt", "a", encoding="UTF-8") as file_log:
        file_log.write(f"{message}!\nВремя: {datetime.datetime.now()}\nИмя файла: {file_path}\n")
        file_log.write(f"Строка: {index + 1}\nСодержание ячейки: {row}\n")


def inventory_runner(file_path: str = "", mode: str = "r", encoding: str = "UTF-8-sig",
                     has_header: bool = False, eof_marker: str = "",
                     file_mask: str = "", delimiter: str = ",",
                     shielding: str = "\"", line_break: str = "\n",
                     decimal_separator: str = ".", bug: bool = False, *fieldnames):
    with (open(file_path, mode, encoding=encoding) as file, \
          open(f"{file_path.split('.')[0]}.json", "w", encoding=encoding) as file_1):
        # Значения по-умолчанию.
        stock_in_days = "0"
        in_transit = "0.000"
        # Словарь для юнитов.
        dict_json = {"items": []}
        # Если отсутствует шапка.
        if not has_header:
            reader = csv.reader(file, delimiter=delimiter)
        else:
            reader = csv.reader(file, delimiter=delimiter)
            next(reader)

        for index, row in enumerate(file):
            row = row.strip().split(",")
            # Переписывание значений.
            if len(row) == 8:
                store_ext_id, price_ext_id, snapshot_datetime, in_matrix, qty, \
                    sell_price, price_cost, min_stock_level = (value for value in row)
            elif len(row) == 10:
                store_ext_id, price_ext_id, snapshot_datetime, in_matrix, qty, \
                    sell_price, price_cost, min_stock_level, stock_in_days, in_transit = (value for value in row)
            else:
                try:
                    store_ext_id, price_ext_id, snapshot_datetime, in_matrix, qty, \
                        sell_price, price_cost, min_stock_level, stock_in_days, in_transit = (value for value in row)
                except ValueError:
                    warning(file_path=file_path, index=index, row=row, message="Ошибка ValueError")
                    bug = True
                    continue
            if len(store_ext_id) >= 41:
                warning(file_path=file_path, index=index, row=row, message=f"шибка превышен размер строки "
                                                                           f"store_ext_id. Длина: {len(store_ext_id)}")
                bug = True
                continue
            if len(price_ext_id) >= 41:
                warning(file_path=file_path, index=index, row=row, message=f"шибка превышен размер строки "
                                                                           f"price_ext_id. Длина: {len(price_ext_id)}")
                bug = True
                continue
            # Проверка на наличие пустой строки.
            # Если есть, то заменить на стандартное значение.
            if stock_in_days == "":
                stock_in_days = "0"
            if in_transit == "":
                in_transit = "0.00"
            dict_json["items"].append(
                {"store_ext_id": store_ext_id,
                 "price_ext_id": price_ext_id,
                 "snapshot_datetime": snapshot_datetime,
                 "in_matrix": in_matrix,
                 "qty": qty,
                 "sell_price": sell_price,
                 "prime_cost": price_cost,
                 "min_stock_level": min_stock_level,
                 "stock_in_days": stock_in_days,
                 "in_transit": in_transit})
        json.dump(dict_json, file_1, separators=(",", ":"), indent="    ")
        if bug:
            return "Работа с файлом завершена, но с ошибкой! Смотрите логи."
    return f"Работа с файлом {file_path} завершена без ошибок!"


def price_runner(file_path: str = "", mode: str = "r", encoding: str = "UTF-8-sig",
                 has_header: bool = False, eof_marker: str = "",
                 file_mask: str = "", delimiter: str = ",",
                 shielding: str = "\"", line_break: str = "\n",
                 decimal_separator: str = ".", bug: bool = False, *fieldnames):
    with (open(file_path, mode, encoding=encoding) as file, \
          open(f"{file_path.split('.')[0]}.json", "w", encoding=encoding) as file_1):
        # Регулярное выражение для разделение наименование продукта, и категорий.
        key_comma_name = r'[1-9A-ZА-Яа-я"%\]\.»],["А-Я]'
        # Словарь для юнитов.
        dict_json = {"items": []}
        for index, row in enumerate(file):
            try:
                find_re = re.split(key_comma_name, row.strip())
                index_categories = len(find_re[0]) + 1
                row_categories = "".join(row[index_categories + 1:].split(",")[::-1][5:]).strip().split("&&")
                name = row[:index_categories]
                row = row.strip().split(",")[::-1]
                categories = row_categories
                price = row[4]
                price_ext_id = row[3]
                vat = row[2]
                unit_type = row[1]
                unit_ratio = row[0]
            except IndexError:
                warning(file_path=file_path, index=index, row=row, message=f"Найден баг!\nОшибка IndexError")
                bug = True
                continue
            dict_json["items"].append(
                {"name": name,
                 "categories": categories,
                 "price": price,
                 "price_ext_id": price_ext_id,
                 "vat": vat,
                 "unit_type": unit_type,
                 "unit_ratio": unit_ratio}
            )
        json.dump(dict_json, file_1, separators=(",", ":"), indent="    ", ensure_ascii=False)
        if bug:
            return "Работа с файлом завершена, но с ошибкой! Смотрите логи."
    return f"Работа с файлом {file_path} завершена без ошибок!"


print(inventory_runner(file_path="inventory2.csv", has_header=True))
print(inventory_runner(file_path="inventory1.csv"))
print(price_runner(file_path="price.csv"))
