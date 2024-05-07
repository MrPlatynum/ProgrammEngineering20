"""
Для своего варианта лабораторной работы 2.16 необходимо дополнительно реализовать
интерфейс командной строки (CLI).
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import os.path
import jsonschema


def validate_data(data, schema):
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False


def add_train(trains, destination, train_number, departure_time):
    """Добавляет информацию о поезде и сохраняет список поездов в файл."""
    train = {
        'название пункта назначения': destination,
        'номер поезда': train_number,
        'время отправления': departure_time,
    }

    trains.append(train)
    trains.sort(key=lambda x: x['название пункта назначения'])
    return trains


def list_trains(trains):
    """Выводит список всех поездов."""
    line = f'+-{"-" * 35}-+-{"-" * 15}-+-{"-" * 25}-+'
    print(line)
    print(f"| {'Название пункта назначения':^35} | {'Номер поезда':^15} | {'Время отправления':^25} |")

    for train in trains:
        print(line)
        print(
            f"| {train['название пункта назначения']:^35} | {train['номер поезда']:^15} | {train['время отправления']:^25} |")
    print(line)


def select_trains(trains, search_time):
    """Выводит поезда, отправляющиеся после указанного времени."""
    found = False
    result = []

    print(f"Поезда, отправляющиеся после {search_time}:")
    for train in trains:
        train_time = train['время отправления']
        if train_time >= search_time:
            result.append(train)
            found = True
    if found:
        return result

    if not found:
        return "Нет поездов, отправляющихся после указанного времени."


def display_help():
    """Выводит справку о доступных командах."""
    print("Список команд:\n")
    print("add - добавить информацию о поезде;")
    print("list - вывести список всех поездов;")
    print("select <время> - вывести поезда, отправляющиеся после указанного времени;")
    print("save <file_name> - сохранить информацию о поездах в файл JSON;")
    print("load <file_name> - загрузить информацию о поездах из файла JSON;")
    print("exit - завершить работу с программой.")


def save_trains(filename, trains):
    """
    Сохранить информацию о поездах в файл JSON.
    """
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(trains, f, ensure_ascii=False, indent=4)


def load_trains(file_name):
    """
    Загрузить информацию о поездах из файла JSON и выполнить валидацию данных.
    """
    train_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "название пункта назначения": {"type": "string"},
                "номер поезда": {"type": "string"},
                "время отправления": {"type": "string", "pattern": "^\\d{2}:\\d{2}$"}
            },
            "required": ["название пункта назначения", "номер поезда", "время отправления"]
        }
    }

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
            if validate_data(data, train_schema):
                return data
            else:
                print("Invalid data format in JSON file.")
    except FileNotFoundError:
        print("File not found")


def main(command_line=None):
    """Основная функция управления программой."""

    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename",
        action="store",
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления поезда.
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new train"
    )
    add.add_argument(
        "-d", "--destination", action="store", required=True, help="The destination's name"
    )
    add.add_argument("-n", "--train_number", action="store", help="The train's number")
    add.add_argument("-t", "--departure_time", action="store", help="The departure time")

    # Создать субпарсер для отображения всех поездов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all trains"
    )

    # Создать субпарсер для выбора поезда.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the train"
    )
    select.add_argument(
        "-t",
        "--departure_time",
        action="store",
        type=str,
        required=True,
        help="The required departure time"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Загрузить все поезда из файла, если файл существует.
    changed_file = False
    if os.path.exists(args.filename):
        trains_list = load_trains(args.filename)
    else:
        trains_list = []

    # Добавить поезд.
    if args.command == "add":
        trains_list = add_train(
            trains_list,
            args.destination,
            args.train_number,
            args.departure_time
        )
        changed_file = True

    # Отобразить все поезда.
    elif args.command == "display":
        list_trains(trains_list)

    # Выбрать требуемый поезд.
    elif args.command == "select":
        selected_trains = select_trains(trains_list, args.departure_time)
        list_trains(selected_trains)

    else:
        print(f"Неизвестная команда {args.command}", file=sys.stderr)

    # Сохранить данные в файл, если список поездов был изменен.
    if changed_file:
        save_trains(args.filename, trains_list)


if __name__ == '__main__':
    main()
