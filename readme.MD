Uruchamianie aplikacji do aktualizacji bazy danych szeregów czasowych na własnej maszynie:
1. Pobrać pythona oraz pip
2. Pobrać aplikację z https://github.com/borysk5/python i rozpakować
3. W linii komend systemu Windows przejść do folderu gdzie znajduje się plik flask_app.py
4. Utworzyć w tym folderze podfolder venv
5. Wpisać komendę "python -m venv venv"
6. Wpisać komendę "pip install -r requirements.txt"
7. Wpisać komendę "python -m flask --app flask_app run"
8. Serwer można używać poprzez wejście na http://localhost:5000/serwer na przeglądarce

Ustawianie połączenie z bazą danych w SQL:
W celu używa opcji korzystania z bazy danych SQL nalezy ustawić w pliku logic.py odpowiednie połączenie.
Przykładowo jeśli chcemy połączyć się z bazą danych PostgreSQL należy:
1. Pobrać PostgreSQL razem z pgAdmin4
2. Uworzyć własny serwer z bazą danych.
3. W pliku logic.py zaktualizować SQLALCHEMY_DATABASE_URI odpowiednią nazwą użytkownika, hasłem, nazwą hosta i bazy danych:
SQLALCHEMY_DATABASE_URI = "postgresql://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
)