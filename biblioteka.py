from __future__ import annotations


class Book:
    """
    Represents a book in the library catalogue.
    Each book has a title, author, and a total number of copies.
    """

    def __init__(self, title: str, author: str, total_copies: int):
        self._title = title
        self._author = author
        self._total_copies = total_copies
        self._available_copies = total_copies

    # Props
    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def total_copies(self) -> int:
        return self._total_copies

    @property
    def available_copies(self) -> int:
        return self._available_copies

    # Methods
    def borrow(self) -> bool:
        """Try to borrow one copy. Returns True on success."""
        if self._available_copies > 0:
            self._available_copies -= 1
            return True
        return False

    def __str__(self) -> str:
        return (
            f"\"{self._title}\" by {self._author} "
            f"(available: {self._available_copies}/{self._total_copies})"
        )


# Klasa bazowa
class User:
    """A class which represents a library user"""

    def __init__(self, login: str, password: str, role: str):
        self._login = login
        self._password = password
        self._role = role

    @property
    def login(self) -> str:
        return self._login

    @property
    def role(self) -> str:
        return self._role

    def check_password(self, password: str) -> bool:
        return self._password == password

    def __str__(self) -> str:
        return f"User({self._login}, role={self._role})"


# Klasy pochodne od USer
class Reader(User):
    """A reader who can borrow books and request extensions."""

    def __init__(self, login: str, password: str):
        super().__init__(login, password, role="reader")
        self._borrowed_books: list[Book] = []
        self._extension_requests: list[Book] = []

    @property
    def borrowed_books(self) -> list["Book"]:
        return list(self._borrowed_books)

    @property
    def extension_requests(self) -> list["Book"]:
        return list(self._extension_requests)

    def add_borrowed(self, book: Book) -> None:
        self._borrowed_books.append(book)

    def request_extension(self, book: Book) -> bool:
        """Request an extension for a borrowed book."""
        if book not in self._borrowed_books:
            return False  # False because the book is not borrowed
        if book in self._extension_requests:
            return False  # False because the extension is already requested
        self._extension_requests.append(book)
        return True

    def remove_extension_request(self, book: Book) -> None:
        if book in self._extension_requests:
            self._extension_requests.remove(book)


class Librarian(User):
    """A librarian with administrative privileges."""

    def __init__(self, login: str, password: str):
        super().__init__(login, password, role="librarian")


class Library:
    def __init__(self):
        self._books: list[Book] = []
        self._users: list[User] = []

    def add_book(self, book: Book) -> None:
        self._books.append(book)

    def add_user(self, user: User) -> None:
        self._users.append(user)

    def authenticate(self, login: str, password: str) -> User | None:
        for user in self._users:
            if user.login == login and user.check_password(password):
                return user
        return None

    def browse_catalogue(self) -> None:
        print("\n--- Book catalogue ---")
        print(f"{'No.':<5}{'Title':<25}{'Author':<25}{'Available copies'}")
        print("-" * 70)
        for idx, book in enumerate(self._books, start=1):
            print(f"{idx:<5}{book.title:<25}{book.author:<25}{book.available_copies}")
        print()

    def borrow_book(self, reader: "Reader") -> None:
        print("\n--- Borrow a book ---")
        title = input("Enter the book title: ").strip()

        book = self._find_book(title)
        if book is None:
            print(f'No book found with the title "{title}".')
            return

        if book.borrow():
            reader.add_borrowed(book)
            print(f'Borrowed: "{book.title}".')
        else:
            print(f'No available copies of "{book.title}".')

    # Reader's borrowed list
    @staticmethod
    def show_borrowings(reader: "Reader") -> None:
        print("\n--- My borrowings ---")
        borrowed = reader.borrowed_books
        if not borrowed:
            print("You have no borrowed books.")
            return
        for idx, book in enumerate(borrowed, start=1):
            print(f"  {idx}. {book.title}")
        print()

    def request_extension(self, reader: "Reader") -> None:
        print("\n--- Request an extension ---")
        borrowed = reader.borrowed_books
        if not borrowed:
            print("You have no borrowed books.")
            return

        for idx, book in enumerate(borrowed, start=1):
            print(f"  {idx}. {book.title}")

        try:
            choice = int(input("Choose a book number: ").strip())
        except ValueError:
            print("Invalid number.")
            return

        if choice < 1 or choice > len(borrowed):
            print("Invalid number.")
            return

        book = borrowed[choice - 1]
        if reader.request_extension(book):
            print(f'Extension request sent for "{book.title}".')
        else:
            print("Extension already requested for this book.")

    def show_all_loans(self) -> None:
        print("\n--- All current loans ---")
        any_loan = False
        for user in self._users:
            if isinstance(user, Reader):
                for book in user.borrowed_books:
                    print(f"  {user.login:<15} -> {book.title}")
                    any_loan = True
        if not any_loan:
            print("  No active loans.")
        print()

    def handle_extension_requests(self) -> None:
        print("\n--- Extension requests ---")

        # Collect all pending requests across readers
        requests: list[tuple[Reader, Book]] = []
        for user in self._users:
            if isinstance(user, Reader):
                for book in user.extension_requests:
                    requests.append((user, book))

        if not requests:
            print("  No pending requests.")
            return

        for idx, (reader, book) in enumerate(requests, start=1):
            print(f"  {idx}. {reader.login} — \"{book.title}\"")

        for reader, book in requests:
            answer = (
                input(
                    f'\nAccept extension for "{book.title}" '
                    f"(reader: {reader.login})? [y/n]: "
                )
                .strip()
                .lower()
            )
            if answer == "y":
                reader.remove_extension_request(book)
                print(f"  Extension ACCEPTED.")
            else:
                reader.remove_extension_request(book)
                print(f"  Extension REJECTED.")

    # --- helper ---

    def _find_book(self, title: str) -> Book | None:
        for book in self._books:
            if book.title.lower() == title.lower():
                return book
        return None


# --------------------------------------------------------------
# MENUS which depend on user's role
# ----------------------------------------------------------------

MAX_ATTEMPTS = 3


def reader_menu(library: Library, reader: Reader) -> None:
    while True:
        print("\n========== READER MENU ==========")
        print("1. Browse a catalogue")
        print("2. Borrow a book")
        print("3. My borrowings")
        print("4. Request an extension")
        print("5. Log out")
        print("=================================")
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            library.browse_catalogue()
        elif choice == "2":
            library.borrow_book(reader)
        elif choice == "3":
            library.show_borrowings(reader)
        elif choice == "4":
            library.request_extension(reader)
        elif choice == "5":
            print(f"\nLogged out user: {reader.login}. See you later!")
            break
        else:
            print("Invalid choice. Please choose an option from 1 to 5.")


def librarian_menu(library: Library, librarian: Librarian) -> None:
    while True:
        print("\n======== LIBRARIAN MENU =========")
        print("1. Browse a catalogue")
        print("2. List all current loans")
        print("3. Handle extension requests")
        print("4. Log out")
        print("=================================")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            library.browse_catalogue()
        elif choice == "2":
            library.show_all_loans()
        elif choice == "3":
            library.handle_extension_requests()
        elif choice == "4":
            print(f"\nLogged out user: {librarian.login}. See you later!")
            break
        else:
            print("Invalid choice. Please choose an option from 1 to 4.")



# ----------------------------------------------------------------
# INITIAL DATA

# ----------------------------------------------------------------

def create_library() -> Library:
    """Creates a Library instance populated with sample books and users."""
    library = Library()

    # Books
    library.add_book(Book("Lalka", "Boleslaw Prus", 3))
    library.add_book(Book("Pan Tadeusz", "Adam Mickiewicz", 2))
    library.add_book(Book("Quo Vadis", "Henryk Sienkiewicz", 1))
    library.add_book(Book("Book 4", "Miki tropiki", 4))
    library.add_book(Book("Book 5", "Mikolaj Stolarz", 2))

    # Readers
    library.add_user(Reader("user1", "password123"))
    library.add_user(Reader("user2", "password123"))
    library.add_user(Reader("user3", "password123"))

    # Librarian
    library.add_user(Librarian("admin", "admin123"))

    return library


# ----------------------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------------------


def main() -> None:
    print("=" * 40)
    print("  WELCOME TO THE LIBRARY SYSTEM")
    print("=" * 40)

    library = create_library()

    while True:
        # Login with attempt limit
        logged_in_user: User | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"\n--- Login (attempt {attempt}/{MAX_ATTEMPTS}) ---")
            login_input = input("Login: ").strip()
            password_input = input("Password: ").strip()

            if login_input.lower() == "quit":
                print("\nThank you for using the library system!")
                return

            logged_in_user = library.authenticate(login_input, password_input)
            if logged_in_user is not None:
                print(f"\nLogged in successfully as: {logged_in_user.login}")
                break
            print("Invalid login or password.")
        else:
            print("\nLogin attempt limit exceeded. Try again.\n")
            continue

        # Role-dependent menu
        if isinstance(logged_in_user, Reader):
            reader_menu(library, logged_in_user)
        elif isinstance(logged_in_user, Librarian):
            librarian_menu(library, logged_in_user)

    print("\nThank you for using the library system!")


if __name__ == "__main__":
    main()
