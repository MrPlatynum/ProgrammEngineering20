"""
Самостоятельно изучите работу с пакетом click для построения интерфейса командной строки
(CLI). Для своего варианта лабораторной работы 2.16 необходимо реализовать интерфейс
командной строки с использованием пакета click.
"""

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import json
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
    click.echo(line)
    click.echo(f"| {'Название пункта назначения':^35} | {'Номер поезда':^15} | {'Время отправления':^25} |")

    for train in trains:
        click.echo(line)
        click.echo(
            f"| {train['название пункта назначения']:^35} | {train['номер поезда']:^15} | {train['время отправления']:^25} |")
    click.echo(line)


def select_trains(trains, search_time):
    """Выводит поезда, отправляющиеся после указанного времени."""
    found = False
    result = []

    click.echo(f"Поезда, отправляющиеся после {search_time}:")
    for train in trains:
        train_time = train['время отправления']
        if train_time >= search_time:
            result.append(train)
            found = True
    if found:
        return result

    if not found:
        return "Нет поездов, отправляющихся после указанного времени."


@click.group()
def cli():
    """Список команд для управления информацией о поездах."""
    pass


@cli.command()
@click.argument('filename', type=click.Path())
@click.option('-d', '--destination', prompt='Название пункта назначения', help='The destination\'s name')
@click.option('-n', '--train_number', prompt='Номер поезда', help='The train\'s number')
@click.option('-t', '--departure_time', prompt='Время отправления', help='The departure time')
def add(filename, destination, train_number, departure_time):
    """Добавить информацию о новом поезде."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            trains_list = json.load(f)
    else:
        trains_list = []

    trains_list = add_train(trains_list, destination, train_number, departure_time)

    save_trains(filename, trains_list)


@cli.command()
@click.argument('filename', type=click.Path())
def display(filename):
    """Вывести список всех поездов."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            trains_list = json.load(f)
            list_trains(trains_list)
    else:
        click.echo("Файл не найден.")


@cli.command()
@click.argument('filename', type=click.Path())
@click.option('-t', '--departure_time', prompt='Время отправления', help='The departure time')
def select(filename, departure_time):
    """Вывести поезда, отправляющиеся после указанного времени."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            trains_list = json.load(f)
            selected_trains = select_trains(trains_list, departure_time)
            if selected_trains:
                list_trains(selected_trains)
            else:
                click.echo("Нет поездов, отправляющихся после указанного времени.")
    else:
        click.echo("Файл не найден.")


def save_trains(filename, trains):
    """
    Сохранить информацию о поездах в файл JSON.
    """
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(trains, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    cli()
