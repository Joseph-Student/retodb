import math
import sys
from collections import OrderedDict
from datetime import datetime

from peewee import *

db = SqliteDatabase('diary.db')


class Entry(Model):
    content = TextField()
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def create_and_connect():
    """Connects to the database and creates the tables"""
    db.connect()
    db.create_tables([Entry], safe=True)


def menu_loop():
    """Show menu"""
    choice = None
    while choice != 'q':
        print("Press 'q' to quit")
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input("Action: ").lower().strip()
        print()
        if choice in menu:
            menu[choice]()


def add_entry():
    """Add entry"""
    print("Enter your thoughts.")
    print("Press ctr + Z on Windows or ctrl + D on Mac to finish")
    data = sys.stdin.read().strip()
    if data:
        if input(
                "Do you want to save your entry? [Yn]").lower().strip() != 'n':
            Entry.create(content=data)
            print("Your entry was saved successfully\n")


def view_entries(search_query=None, paginate_by=5, page=1):
    """View all entries"""
    entries = Entry.select().order_by(Entry.timestamp.desc())
    if isinstance(search_query, str):
        entries = entries.where(Entry.content.contains(search_query))
    elif isinstance(search_query, datetime):
        entries = entries.where(Entry.timestamp <= search_query)
    page_cant = math.ceil(entries.count() / paginate_by)
    if page:
        entries = entries.paginate(page, paginate_by)
    record = 0
    for entry in entries:
        record += 1
        print("Page {0} of {1}.".format(page, page_cant))
        print("Entry {0} of {1}.\n".format(record, entries.count()))
        timestamp = entry.timestamp.strftime('%A %B %d, %Y %I:%M%p')
        print(timestamp)
        print('+' * len(timestamp))
        print('\n')
        print(entry.content)
        print('\n')
        print('+' * len(timestamp))
        print('n) next entry')
        print('p) next page')
        print('e) edit entry')
        print('d) delete entry')
        print('q) return to menu')
        next_action = input("Action:[Npedq] ").lower().strip()
        print()
        if next_action == 'q':
            break
        elif next_action == 'd':
            delete_entry(entry)
        elif next_action == 'p':
            view_entries(search_query=search_query, page=page + 1)
            break
        elif next_action == 'e':
            edit_entry(entry)
    else:
        if page < page_cant:
            view_entries(search_query=search_query, page=page + 1)
        else:
            print("No hay mas entradas.\n")


def edit_entry(entry):
    """Edit entry"""
    print("Texto viejo.")
    sys.stdout.write("{0}\n".format(entry.content))
    print("Escriba el texto nuevo: \n")
    new_content = sys.stdin.read().strip()
    entry.content = new_content
    entry.save()
    print()
    print("Entrada guardada correctamente.\n")


def search_entries():
    """Search Entries"""
    search_query = input("Search query: ").strip()
    print()
    view_entries(search_query)


def search_for_date_entries():
    """Search for date in entries"""
    try:
        search_date = datetime.strptime(
            input("Search date query: [YYYY-mm-dd]\n").strip(),
            '%Y-%m-%d'
        ).date()
    except TypeError:
        print(
            "No coloco una fecha valida. Por favor introducir fecha con el "
            "formato indicado 'YYYY-mm-dd'."
        )
        search_for_date_entries()
    else:
        view_entries(search_date)


def delete_entry(entry):
    """Delete an Entry"""
    action = input("Are you sure?[Yn] ").lower().strip()
    print()
    if action == 'y':
        entry.delete_instance()


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ('s', search_entries),
    ('t', search_for_date_entries)
])


if __name__ == '__main__':
    create_and_connect()
    menu_loop()
