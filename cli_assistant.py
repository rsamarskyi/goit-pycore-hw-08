from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
            self.value = value


class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits.")

        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(birthday)

        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        found_phone = self.find_phone(phone)

        if found_phone:
            self.phones.remove(found_phone)

    def edit_phone(self, old_phone, new_phone):
        found_phone = self.find_phone(old_phone)

        if found_phone is None:
            raise ValueError("Phone not found.")

        new_phone = Phone(new_phone)
        found_phone.value = new_phone.value

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj

        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(phone.value for phone in self.phones)

        if self.birthday:
            birthday = self.birthday.value.strftime("%d.%m.%Y")
        else:
            birthday = "not set"

        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones}, "
            f"birthday: {birthday}"
        )


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value.casefold()] = record

    def find(self, name):
        return self.data.get(name.casefold())

    def delete(self, name):
        self.data.pop(name.casefold(), None)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():

            if record.birthday is None:
                continue

            birthday = record.birthday.value.date()

            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1
                )

            days_difference = (birthday_this_year - today).days

            if 0 <= days_difference < 7:

                # Saturday
                if birthday_this_year.weekday() == 5:
                    congratulation_date = birthday_this_year + timedelta(days=2)

                # Sunday
                elif birthday_this_year.weekday() == 6:
                    congratulation_date = birthday_this_year + timedelta(days=1)

                else:
                    congratulation_date = birthday_this_year

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date":
                        congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as e:
            return str(e)

        except KeyError:
            return "Contact not found."

        except IndexError:
            return "Enter user name."

    return inner


def parse_input(user_input):
    parts = user_input.strip().split()

    if not parts:
        return "", []

    command = parts[0].casefold()
    args = parts[1:]

    return command, args


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")

    name, phone, *_ = args

    record = book.find(name)

    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)

    return message


@input_error
def change_phone(args, book):
    if len(args) < 3:
        raise ValueError(
            "Give me name, old phone and new phone please."
        )

    name, old_phone, new_phone, *_ = args

    record = book.find(name)

    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)

    return f"Contact {record.name.value} was updated."


@input_error
def show_phone_number(args, book):
    name = args[0]

    record = book.find(name)

    if record is None:
        raise KeyError

    if not record.phones:
        return f"{record.name.value} has no phone numbers."

    phones = "; ".join(
        phone.value for phone in record.phones
    )

    return f"Phone number for {record.name.value}: {phones}"


@input_error
def show_all_contacts(book):
    if not book.data:
        return "Your contact book is empty."

    return "\n".join(
        str(record)
        for record in book.data.values()
    )


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Give me name and birthday please.")

    name, birthday, *_ = args

    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)

    return f"Birthday added for {record.name.value}."


@input_error
def show_birthday(args, book):
    name = args[0]

    record = book.find(name)

    if record is None:
        raise KeyError

    if record.birthday is None:
        return f"Birthday for {record.name.value} is not set."

    birthday = record.birthday.value.strftime("%d.%m.%Y")

    return f"{record.name.value}'s birthday is {birthday}."


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    return "\n".join(
        f"{person['name']}: {person['congratulation_date']}"
        for person in upcoming
    )

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()

    print("Welcome to the assistant bot!")

    try:
        while True:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)

            if command in ("close", "exit"):
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_phone(args, book))

            elif command == "phone":
                print(show_phone_number(args, book))

            elif command == "all":
                print(show_all_contacts(book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                print(birthdays(args, book))

            else:
                print("Invalid command.")

    finally:
        save_data(book)

if __name__ == "__main__":
    main()