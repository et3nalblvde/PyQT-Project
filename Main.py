import os
import sqlite3
import sys
import random
from PyQt6 import QtWidgets, QtGui, QtCore, QtSql
from PyQt6.QtCore import QUrl
from PyQt6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt6.QtWidgets import QMessageBox
import pandas as pd
from config import users, data, posters, icons
import hashlib




class PasswordLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.show_password = False

        self.show_password_button = QtWidgets.QPushButton(self)
        self.show_password_button.setIcon(QtGui.QIcon(f'{icons}/closed_eye_icon.png'))
        self.show_password_button.setStyleSheet("border: none; background: transparent;")
        self.show_password_button.setFixedSize(24, 24)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)

        self.show_password_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        self.update_button_position()

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Normal if self.show_password else QtWidgets.QLineEdit.EchoMode.Password)
        icon_name = 'open_eye_icon.png' if self.show_password else 'closed_eye_icon.png'
        self.show_password_button.setIcon(QtGui.QIcon(f'{icons}/{icon_name}'))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_button_position()

    def update_button_position(self):
        button_x = self.width() - self.show_password_button.width() - 5
        button_y = (self.height() - self.show_password_button.height()) // 2
        self.show_password_button.move(button_x, button_y)
        self.show_password_button.raise_()


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QtGui.QIcon(f'{icons}/sign in.png'))

        self.setWindowTitle("Вход")
        self.setGeometry(200, 200, 350, 250)
        self.setStyleSheet("background-color: #FFE4E1;")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title_label = QtWidgets.QLabel("Вход", self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        self.layout.addWidget(self.title_label)

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.username_input)
        self.layout.addSpacing(12)

        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.password_input)

        self.forgot_password_link = QtWidgets.QLabel("Забыли пароль?", self)
        self.forgot_password_link.setStyleSheet(
            "color: #1E90FF; font-size: 14px; text-decoration: underline; cursor: pointer;")
        self.forgot_password_link.mousePressEvent = self.open_password_recovery_window
        self.forgot_password_link.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.forgot_password_link.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.forgot_password_link, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.layout.addSpacing(5)

        self.login_button = QtWidgets.QPushButton("Войти", self)
        self.login_button.setStyleSheet(""" 
            QPushButton {
                background-color: #4CAF50;  
                color: white; 
                padding: 10px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                cursor: pointer;
            }
        """)
        self.login_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.registration_link = QtWidgets.QLabel("У вас нет аккаунта? Зарегистрироваться", self)
        self.registration_link.setStyleSheet(
            "color: #1E90FF; font-size: 14px; text-decoration: underline; cursor: pointer;")
        self.registration_link.mousePressEvent = self.open_registration_window
        self.registration_link.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.registration_link.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.registration_link)

        self.layout.addStretch()

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            with open(users, newline='', encoding='utf-8') as csvfile:
                next(csvfile)
                for line in csvfile:
                    name, user, pwd = line.strip().split('|')
                    if user == username and pwd == hashed_password:
                        QMessageBox.information(self, "Успех", f"Добро пожаловать, {name}!")
                        self.accept()
                        self.personal_cabinet = PersonalCabinet(username, self)
                        self.personal_cabinet.show()
                        self.main_window = MainWindow(username)
                        return

                QMessageBox.warning(self, "Ошибка", "Неправильное имя пользователя или пароль")

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл пользователей не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def open_registration_window(self, event=None):
        registration_dialog = RegistrationWindow(self)
        registration_dialog.show()

    def open_password_recovery_window(self, event=None):
        recovery_dialog = PasswordRecoveryDialog(self)
        recovery_dialog.exec()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class RegistrationWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QtGui.QIcon(f'{icons}/log in.png'))
        self.setWindowTitle("Регистрация")
        self.setGeometry(200, 200, 350, 300)
        self.setStyleSheet("background-color: #FFE4E1;")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title_label = QtWidgets.QLabel("Регистрация", self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-family: 'Roboto';
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        self.layout.addWidget(self.title_label)

        self.name_input = QtWidgets.QLineEdit(self)
        self.name_input.setPlaceholderText("Имя")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.name_input)

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.username_input)

        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.password_input)

        self.layout.addSpacing(15)

        self.register_button = QtWidgets.QPushButton("Зарегистрироваться", self)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px; 
                font-weight: bold; 
            }
            QPushButton:hover {
                background-color: #45a049;
                cursor: pointer; 
            }
        """)
        self.register_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.layout.addStretch()
        self.create_users_file()

    def create_users_file(self):
        if not os.path.exists(users):
            with open(users, 'w', encoding='utf-8') as csvfile:
                csvfile.write("# Имя|Имя пользователя|Пароль\n")

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        name = self.name_input.text().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if " " in username:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя не должно содержать пробелы.")
            return

        try:
            user_exists = False
            with open(users, 'r', encoding='utf-8') as csvfile:
                next(csvfile)
                for line in csvfile:
                    _, user, _ = line.strip().split('|')
                    if user == username:
                        user_exists = True
                        break

            if user_exists:
                QMessageBox.warning(self, "Ошибка", "Имя пользователя уже существует.")
                return

            with open(users, 'a', encoding='utf-8') as csvfile:
                csvfile.write(f"{name}|{username}|{hashed_password}\n")

            self.create_user_movies_database(username)
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.accept()

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл пользователей не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def create_user_movies_database(self, username):
        new_database_path = f"Database/Movies_{username}.db"
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(new_database_path)

        if db.open():
            query = QSqlQuery(db)

            query.exec(""" CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            ); """)
            query.exec(""" CREATE TABLE IF NOT EXISTS MovieGenres (
                movie_id INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (genre_id) REFERENCES genres(id)
            ); """)
            query.exec(""" CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                original_title TEXT,
                average_rating REAL,
                genres TEXT,
                num_votes INTEGER,
                year INTEGER,
                film_link TEXT,
                poster_link TEXT,
                description TEXT,
                favorite INTEGER
            ); """)

            original_db = QSqlDatabase.addDatabase("QSQLITE", "original_db")
            original_db.setDatabaseName(f'{data}/movies.db')
            if original_db.open():
                original_query = QSqlQuery(original_db)

                original_query.exec("SELECT * FROM genres;")
                while original_query.next():
                    genre_id = original_query.value(0)
                    genre = original_query.value(1)
                    query.exec(f"INSERT INTO genres (id, name) VALUES ({genre_id}, '{genre}');")

                original_query.exec("SELECT * FROM MovieGenres;")
                while original_query.next():
                    movie_id = original_query.value(0)
                    genre_id = original_query.value(1)
                    query.exec(f"INSERT INTO MovieGenres (movie_id, genre_id) VALUES ({movie_id}, {genre_id});")

                original_query.exec("SELECT * FROM movies;")
                while original_query.next():
                    id = original_query.value(0)
                    title = original_query.value(1)
                    original_title = original_query.value(2)
                    average_rating = original_query.value(3)
                    genres = original_query.value(4)
                    num_votes = original_query.value(5)
                    year = original_query.value(6)
                    film_link = original_query.value(7)
                    poster_link = original_query.value(8)
                    description = original_query.value(9)
                    favorite = original_query.value(10)
                    query.exec(
                        f"INSERT INTO movies (id, title, original_title, average_rating, genres, num_votes, year, film_link, poster_link, description, favorite) "
                        f"VALUES ({id}, '{title}', '{original_title}', {average_rating}, '{genres}', {num_votes}, {year}, '{film_link}', '{poster_link}', '{description}', {favorite});"
                    )

                original_db.close()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось открыть оригинальную базу данных.")
                return False

            if query.lastError().isValid():
                QMessageBox.critical(self, "Ошибка", query.lastError().text())
                return False
            return True
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть новую базу данных.")
            return False


class PasswordRecoveryDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Восстановление пароля")
        self.setGeometry(200, 200, 300, 200)

        self.setStyleSheet("background-color: #FFE4E1;")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title_label = QtWidgets.QLabel("Восстановление пароля", self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        self.layout.addWidget(self.title_label)

        self.name_input = QtWidgets.QLineEdit(self)
        self.name_input.setPlaceholderText("Имя")
        self.name_input.setFixedHeight(40)
        self.name_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.name_input)

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.username_input)

        self.new_password_input = QtWidgets.QLineEdit(self)
        self.new_password_input.setPlaceholderText("Новый пароль")
        self.new_password_input.setFixedHeight(40)
        self.new_password_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        self.layout.addWidget(self.new_password_input)

        self.recover_button = QtWidgets.QPushButton("Сменить пароль", self)
        self.recover_button.setStyleSheet(""" 
            QPushButton {
                background-color: #4CAF50;  
                color: white; 
                padding: 10px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                cursor: pointer;
            }
        """)
        self.recover_button.clicked.connect(self.recover_password)
        self.layout.addWidget(self.recover_button)

        self.layout.addStretch()

    def recover_password(self):

        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        new_password = self.new_password_input.text()

        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

        try:
            lines = []
            user_found = False

            with open(users, 'r', encoding='utf-8') as csvfile:
                for line in csvfile:
                    user_data = line.strip().split('|')
                    if len(user_data) == 3:
                        stored_name, stored_user, stored_pwd = user_data

                        if stored_user == username and stored_name == name:
                            lines.append(f"{stored_name}|{stored_user}|{hashed_new_password}\n")
                            user_found = True
                        else:
                            lines.append(line)
                    else:
                        lines.append(line)

            if not user_found:
                QMessageBox.warning(self, "Ошибка", "Имя пользователя или имя неверны.")
                return

            with open(users, 'w', encoding='utf-8') as csvfile:
                csvfile.writelines(lines)

            QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            self.accept()

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл пользователей не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setupUi()
        self.connect_to_database()
        self.load_data()
        self.profile_button.setText(f"{self.username}")
        self.profile_button.clicked.connect(self.toggle_window)
        self.setFixedSize(1100, 1000)
        self.setStyleSheet("background-color: #FFE4E1;")
        self.setWindowIcon(QtGui.QIcon(f'{icons}/film.png'))

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("Фильмы")
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.centralwidget)

        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        menubar = self.menuBar()
        add_movie_menu = menubar.addMenu("Добавить фильм")
        add_movie_action = QtGui.QAction("Добавить новый фильм", self)
        add_movie_action.triggered.connect(self.open_add_movie_window)
        add_movie_menu.addAction(add_movie_action)

        self.profile_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.profile_button.setIcon(QtGui.QIcon(f'{icons}/avatar.jpeg'))
        self.profile_button.setIconSize(QtCore.QSize(40, 40))
        self.profile_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.profile_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.profile_button)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        self.ExportButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.ExportButton.setText("Экспорт в Excel")
        self.ExportButton.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ExportButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.ExportButton.clicked.connect(self.export_to_excel)
        self.button_layout.addWidget(self.ExportButton)

        self.refresh_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.refresh_button.setIcon(QtGui.QIcon(f'{icons}/refresh.png'))
        self.refresh_button.setIconSize(QtCore.QSize(20, 20))
        self.refresh_button.setText("Обновить")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.refresh_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_database)
        self.button_layout.addWidget(self.refresh_button)

        self.layout.addLayout(self.button_layout)

        self.search_layout = QtWidgets.QHBoxLayout()
        self.search_layout.setSpacing(10)
        self.search_layout.setContentsMargins(0, 0, 0, 0)

        self.SearchWindow = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.SearchWindow.setPlaceholderText("Введите название фильма...")
        self.SearchWindow.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 10px;
            }
        """)
        self.search_layout.addWidget(self.SearchWindow)

        self.SearchButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.SearchButton.setText("🔎")
        self.SearchButton.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.SearchButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.search_layout.addWidget(self.SearchButton)
        self.layout.addLayout(self.search_layout)

        self.sort_date_combo = QtWidgets.QComboBox(parent=self.centralwidget)
        self.sort_date_combo.addItems(["Сортировать по дате", "По возрастанию", "По убыванию"])
        self.sort_date_combo.currentIndexChanged.connect(self.handle_sorting)
        self.layout.addWidget(self.sort_date_combo)

        self.sort_alpha_combo = QtWidgets.QComboBox(parent=self.centralwidget)
        self.sort_alpha_combo.addItems(["Сортировать по алфавиту", "A-Z", "Z-A"])
        self.sort_alpha_combo.currentIndexChanged.connect(self.handle_sorting)
        self.layout.addWidget(self.sort_alpha_combo)

        self.FilterButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.FilterButton.setText("Фильтрация")
        self.FilterButton.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.FilterButton.clicked.connect(self.open_filter_window)
        self.FilterButton.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.FilterButton)

        self.MovieTable = QtWidgets.QTableView(parent=self.centralwidget)
        self.MovieTable.setStyleSheet("""
            QTableView {
                background-color: #f0f0f0;
                border: 2px solid #ddd;
                gridline-color: #ccc;
                font-size: 14px;
                selection-background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: none;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(self.MovieTable)

        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setStyleSheet("background-color: #f0f0f0; border-top: 1px solid #ccc;")
        self.setStatusBar(self.statusbar)

        self.SearchWindow.textChanged.connect(self.filter_movies)
        self.SearchButton.clicked.connect(self.filter_movies)
        self.MovieTable.doubleClicked.connect(self.show_film_details)

    def connect_to_database(self):
        database_name = f"Database/Movies_{self.username}.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(database_name)
        if not self.db.open():
            self.statusbar.showMessage("Не удалось подключиться к базе данных.")

    def open_add_movie_window(self):
        self.add_movie_window = AddMovieWindow(self.username)
        self.add_movie_window.show()

    def open_filter_window(self):

        filter_window = FilterWindow(self.apply_sorting)
        filter_window.exec()

    def load_data(self):
        self.apply_sorting()

    def apply_sorting(self, selected_genres=[]):
        search_text = self.SearchWindow.text().strip()
        date_sort_order = self.sort_date_combo.currentIndex()
        alpha_sort_order = self.sort_alpha_combo.currentIndex()

        query_string = f"""
            SELECT title AS 'Фильм', original_title AS 'Оригинальное название', average_rating AS 'Рейтинг',
                   num_votes AS 'Голоса', year AS 'Дата', genres AS 'Жанр', film_link, poster_link, description, favorite
            FROM movies m
            LEFT JOIN moviegenres mg ON m.id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.id
        """

        filters = []

        if search_text:
            filters.append(
                f" (UPPER(m.title) LIKE UPPER('%{search_text}%') OR UPPER(m.original_title) LIKE UPPER('%{search_text}%'))"
            )

        if selected_genres:
            genre_placeholders = ', '.join(['?'] * len(selected_genres))
            filters.append(f" g.name IN ({genre_placeholders})")

        if filters:
            query_string += " WHERE " + " AND ".join(filters)

        query_string += " GROUP BY m.id"

        if selected_genres:
            query_string += f" HAVING COUNT(DISTINCT g.id) = {len(selected_genres)}"

        order_clauses = []
        if date_sort_order == 1:
            order_clauses.append("m.year ASC")
        elif date_sort_order == 2:
            order_clauses.append("m.year DESC")

        if alpha_sort_order == 1:
            order_clauses.append("m.title ASC")
        elif alpha_sort_order == 2:
            order_clauses.append("m.title DESC")

        if order_clauses:
            query_string += " ORDER BY " + ", ".join(order_clauses)

        query = QSqlQuery()
        query.prepare(query_string)

        for i, genre in enumerate(selected_genres):
            query.bindValue(i, genre)

        if not query.exec():
            self.statusbar.showMessage("Ошибка выполнения запроса: " + query.lastError().text())
            return

        self.model = QSqlQueryModel()
        self.model.setQuery(query)

        if self.model.lastError().isValid():
            self.statusbar.showMessage("Ошибка выполнения запроса: " + self.model.lastError().text())
            return

        self.MovieTable.setModel(self.model)

        self.MovieTable.setColumnHidden(6, True)
        self.MovieTable.setColumnHidden(7, True)
        self.MovieTable.setColumnHidden(8, True)
        self.MovieTable.setColumnHidden(9, True)
        self.MovieTable.setColumnHidden(10, True)

        column_widths = [225, 225, 70, 70, 70, 350]
        for i, width in enumerate(column_widths):
            self.MovieTable.setColumnWidth(i, width)

        self.MovieTable.setSortingEnabled(True)

    def filter_movies(self):
        self.apply_sorting()

    def handle_sorting(self):
        if (self.sort_date_combo.currentIndex() > 0 and self.sort_alpha_combo.currentIndex() > 0):
            QtWidgets.QMessageBox.warning(self, "Ошибка сортировки", "Нельзя использовать две сортировки одновременно.")
            self.sort_alpha_combo.setCurrentIndex(0)
        else:
            self.apply_sorting()

    def refresh_database(self):
        try:
            self.load_data()
            self.statusbar.showMessage("Данные успешно обновлены!")
        except Exception as e:
            self.statusbar.showMessage(f"Ошибка при обновлении данных: {str(e)}")

    def show_film_details(self, index):
        if index.isValid():
            title = self.model.data(self.model.index(index.row(), 0))
            year = self.model.data(self.model.index(index.row(), 4))
            rating = self.model.data(self.model.index(index.row(), 2))
            film_link = self.model.data(self.model.index(index.row(), 6))
            poster_link = f"{posters}/{title}.jpeg"
            description = self.model.data(self.model.index(index.row(), 8))
            genre = self.model.data(self.model.index(index.row(), 5))

            details_window = FilmDetailsWindow(title, year, rating, film_link, poster_link, description, genre,
                                               self.username)
            details_window.show()

    def export_to_excel(self):
        try:
            movies_data = []
            for row in range(self.model.rowCount()):
                movie = {
                    'Фильм': self.model.data(self.model.index(row, 0)),
                    'Оригинальное название': self.model.data(self.model.index(row, 1)),
                    'Рейтинг': self.model.data(self.model.index(row, 2)),
                    'Голоса': self.model.data(self.model.index(row, 3)),
                    'Дата': self.model.data(self.model.index(row, 4)),
                    'Жанр': self.model.data(self.model.index(row, 5)),
                }
                movies_data.append(movie)

            df = pd.DataFrame(movies_data)
            if not df.empty:
                file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить файл", "",
                                                                     "Excel Files (*.xlsx);;All Files (*)")
                if file_path:
                    df.to_excel(file_path, index=False)
                    self.statusbar.showMessage("Экспорт завершен успешно!")
            else:
                self.statusbar.showMessage("Нет данных для экспорта.")
        except Exception as e:
            self.statusbar.showMessage(f"Ошибка экспорта: {str(e)}")

    def toggle_window(self):
        if self.isHidden():
            self.show()
            self.activateWindow()
        else:
            self.hide()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class FilterWindow(QtWidgets.QDialog):
    def __init__(self, apply_filter_callback):
        super().__init__()
        self.apply_filter_callback = apply_filter_callback
        self.setWindowTitle("Фильтрация по жанрам")
        self.setFixedSize(900, 900)
        self.setStyleSheet("background-color: #FFE4E1;")
        self.setWindowIcon(QtGui.QIcon(f'{icons}/filter.png'))
        self.layout = QtWidgets.QVBoxLayout(self)

        self.genre_label = QtWidgets.QLabel("Выберите жанры:")
        self.layout.addWidget(self.genre_label)

        self.genres = {
            "Экшн": QtWidgets.QCheckBox("Экшн"),
            "Приключения": QtWidgets.QCheckBox("Приключения"),
            "Анимация": QtWidgets.QCheckBox("Анимация"),
            "Биография": QtWidgets.QCheckBox("Биография"),
            "Комедия": QtWidgets.QCheckBox("Комедия"),
            "Криминал": QtWidgets.QCheckBox("Криминал"),
            "Документальный": QtWidgets.QCheckBox("Документальный"),
            "Драма": QtWidgets.QCheckBox("Драма"),
            "Семейный": QtWidgets.QCheckBox("Семейный"),
            "Фэнтези": QtWidgets.QCheckBox("Фэнтези"),
            "Нуар": QtWidgets.QCheckBox("Нуар"),
            "Исторический": QtWidgets.QCheckBox("Исторический"),
            "Ужасы": QtWidgets.QCheckBox("Ужасы"),
            "Мюзикл": QtWidgets.QCheckBox("Мюзикл"),
            "Мистика": QtWidgets.QCheckBox("Мистика"),
            "Романтика": QtWidgets.QCheckBox("Романтика"),
            "Научная фантастика": QtWidgets.QCheckBox("Научная фантастика"),
            "Короткометражный": QtWidgets.QCheckBox("Короткометражный"),
            "Спорт": QtWidgets.QCheckBox("Спорт"),
            "Триллер": QtWidgets.QCheckBox("Триллер"),
            "Война": QtWidgets.QCheckBox("Война"),
            "Вестерн": QtWidgets.QCheckBox("Вестерн"),
            "Супергеройский": QtWidgets.QCheckBox("Супергеройский"),
            "Музыкальный": QtWidgets.QCheckBox("Музыкальный"),
            "Постапокалиптика": QtWidgets.QCheckBox("Постапокалиптика"),
            "Фантастика": QtWidgets.QCheckBox("Фантастика"),
            "Сказка": QtWidgets.QCheckBox("Сказка"),
            "Политический": QtWidgets.QCheckBox("Политический"),
            "Антиутопия": QtWidgets.QCheckBox("Антиутопия"),
            "Артхаус": QtWidgets.QCheckBox("Артхаус"),
            "Комикс": QtWidgets.QCheckBox("Комикс"),
            "Шпионский": QtWidgets.QCheckBox("Шпионский"),
            "Детектив": QtWidgets.QCheckBox("Детектив"),
        }

        for checkbox in self.genres.values():
            self.layout.addWidget(checkbox)

        self.apply_button = QtWidgets.QPushButton("Применить фильтрацию", self)
        self.apply_button.clicked.connect(self.apply_filter)
        self.layout.addWidget(self.apply_button)

    def apply_filter(self):
        selected_genres = [genre for genre, checkbox in self.genres.items() if checkbox.isChecked()]

        if not selected_genres:
            self.apply_filter_callback([])
            self.close()
            return

        genre_placeholders = ', '.join(['?'] * len(selected_genres))
        sql_query = f"""
        SELECT m.*
        FROM movies m
        JOIN moviegenres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name IN ({genre_placeholders})
        GROUP BY m.id
        HAVING COUNT(DISTINCT g.id) = {len(selected_genres)}
        """

        self.apply_filter_callback(selected_genres)

        self.close()


class FavoritesDialog(QtWidgets.QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Избранное")
        self.setStyleSheet("background-color: #f5f5f5; font-size: 14px;")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet("background-color: #FFE4E1;")
        self.favorites_table = QtWidgets.QTableView(self)
        self.setWindowIcon(QtGui.QIcon(f'{icons}/favorite1.png'))
        self.favorites_table.setStyleSheet("""
            QTableView {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.favorites_table)

        self.load_favorites()
        self.adjust_table_size()

        self.favorites_table.doubleClicked.connect(self.show_film_details)

    def open_favorites(self):
        self.show()

    def connect_to_database(self):
        database_name = f"Database/Movies_{self.username}.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(database_name)
        if not self.db.open():
            self.statusbar.showMessage("Не удалось подключиться к базе данных.")

    def load_favorites(self):
        self.connect_to_database()
        query = f"""
            SELECT title AS 'Фильм', original_title AS 'Оригинальное название', average_rating AS 'Рейтинг', 
                   num_votes AS 'Голоса', year AS 'Дата', genres AS 'Жанр', film_link, poster_link, description
            FROM movies
            WHERE favorite = 1
        """
        model = QSqlQueryModel()
        model.setQuery(query)

        if model.lastError().isValid():
            QtWidgets.QMessageBox.critical(self, "Ошибка базы данных", model.lastError().text())
            return

        self.favorites_table.setModel(model)
        self.favorites_table.setColumnHidden(6, True)
        self.favorites_table.setColumnHidden(7, True)
        self.favorites_table.setColumnHidden(8, True)

    def adjust_table_size(self):
        self.favorites_table.resizeColumnsToContents()
        self.favorites_table.horizontalHeader().setStretchLastSection(True)
        self.resize(self.favorites_table.sizeHint().width() + 500, self.favorites_table.sizeHint().height() + 80)

    def show_film_details(self, index):
        if index.isValid():
            title = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 0))
            year = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 4))
            rating = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 2))
            film_link = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 6))
            poster_link = f"{posters}/{title}.jpeg"
            description = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 8))
            genre = self.favorites_table.model().data(self.favorites_table.model().index(index.row(), 5))
            details_window = FilmDetailsWindow(title, year, rating, film_link, poster_link, description, genre,
                                               self.username)
            details_window.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class FilmDetailsWindow(QtWidgets.QDialog):
    def __init__(self, title, year, rating, film_link, poster_link, description, genre, username):
        super().__init__()
        self.setWindowTitle("Информация о фильме")
        self.setWindowIcon(QtGui.QIcon(f'{icons}/details.png'))
        self.setGeometry(100, 100, 400, 550)
        self.username = username
        self.setStyleSheet("background-color: #FFE4E1;")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        button_layout = QtWidgets.QGridLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)

        delete_button = QtWidgets.QPushButton()
        delete_button.setIcon(QtGui.QIcon(f'{icons}/trash.png'))
        delete_button.setIconSize(QtCore.QSize(30, 30))
        delete_button.setStyleSheet(""" 
                    background-color: #FF6F61;  
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                """)
        delete_button.setFixedSize(50, 50)
        delete_button.clicked.connect(lambda: self.confirm_delete(title))
        button_layout.addWidget(delete_button, 0, 0,
                                QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        delete_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        edit_button = QtWidgets.QPushButton()
        edit_button.setIcon(QtGui.QIcon(f'{icons}/edit.png'))
        edit_button.setIconSize(QtCore.QSize(30, 30))
        edit_button.setStyleSheet(""" 
            background-color: #FFC107; 
            border: none; 
            border-radius: 8px; 
            padding: 10px;
        """)
        edit_button.setFixedSize(50, 50)
        edit_button.clicked.connect(
            lambda: self.edit_movie(title, year, rating, film_link, poster_link, description, genre))
        button_layout.addWidget(edit_button, 0, 1,
                                QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight)
        edit_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        layout.addLayout(button_layout)

        title_label = QtWidgets.QLabel(title)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333;")
        layout.addWidget(title_label)

        poster_label = QtWidgets.QLabel()
        if QtCore.QFile.exists(poster_link):
            pixmap = QtGui.QPixmap(poster_link).scaled(200, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            poster_label.setPixmap(pixmap)
        else:
            default_poster_link = f'{posters}/404.jpeg'
            pixmap = QtGui.QPixmap(default_poster_link).scaled(200, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            poster_label.setPixmap(pixmap)

        poster_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(poster_label)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(8)

        year_label = QtWidgets.QLabel(f"Год: {year if year else 'Не указано'}")
        rating_label = QtWidgets.QLabel(f"Рейтинг: {rating if rating else 'Не указано'}")
        description_label = QtWidgets.QLabel(f"{description if description else 'Не указано'}")
        description_label.setWordWrap(True)

        for label in [year_label, rating_label, description_label]:
            label.setStyleSheet("font-size: 14px; color: #555; padding: 5px;")
            info_layout.addWidget(label)

        film_link_button = self.create_button("Смотреть фильм", "#4CAF50", "#388E3C")
        film_link_button.clicked.connect(lambda: self.open_film_link(film_link))
        info_layout.addWidget(film_link_button)

        favorite_button = self.create_button("", "#FF9800", "#F57C00")
        self.update_favorite_button(favorite_button, title)
        favorite_button.clicked.connect(lambda: self.toggle_favorites(title, favorite_button))
        info_layout.addWidget(favorite_button)

        close_button = self.create_button("Закрыть", "#f44336", "#D32F2F")
        close_button.clicked.connect(self.hide)
        info_layout.addWidget(close_button)

        layout.addLayout(info_layout)

        self.setStyleSheet(""" 
            background-color: #f9f9f9; 
            border-radius: 10px;
            border: 1px solid #ddd;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
        """)

        button_height = 40
        for button in [film_link_button, favorite_button, close_button]:
            button.setFixedHeight(button_height)

    def get_genre_id(self, genre_name):
        """Получаем ID жанра по его имени."""
        query = QtSql.QSqlQuery()
        query.prepare("SELECT id FROM genres WHERE name = ?")
        query.addBindValue(genre_name)
        query.exec()

        if query.next():
            return query.value(0)
        else:
            print(f"Genre '{genre_name}' not found.")
        return None

    def link_movie_to_genre(self, movie_id, genre_id):
        """Связываем фильм с жанром через таблицу moviegenres."""
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO moviegenres (movie_id, genre_id) VALUES (?, ?)")
        query.addBindValue(movie_id)
        query.addBindValue(genre_id)

        if not query.exec():
            print(f"Error linking movie {movie_id} to genre {genre_id}: {query.lastError().text()}")

    def edit_movie(self, title, year, rating, film_link, poster_link, description, genre):
        edit_dialog = QtWidgets.QDialog(self)
        edit_dialog.setWindowTitle("Редактировать информацию о фильме")
        edit_dialog.setGeometry(200, 200, 350, 400)
        edit_dialog.setStyleSheet("background-color: #FFE4E1;")

        layout = QtWidgets.QVBoxLayout(edit_dialog)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        title_label = QtWidgets.QLabel("Редактирование фильма")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)
        layout.addWidget(title_label)

        title_input = QtWidgets.QLineEdit(title)
        title_input.setPlaceholderText("Название")
        title_input.setFixedHeight(40)
        title_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        layout.addWidget(title_input)

        year_input = QtWidgets.QLineEdit(str(year))
        year_input.setPlaceholderText("Год")
        year_input.setFixedHeight(40)
        year_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        layout.addWidget(year_input)

        rating_input = QtWidgets.QLineEdit(str(rating))
        rating_input.setPlaceholderText("Рейтинг")
        rating_input.setFixedHeight(40)
        rating_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        layout.addWidget(rating_input)

        genre_input_layout = QtWidgets.QVBoxLayout()

        genre_list = [
            "Экшн", "Приключения", "Анимация", "Биография", "Комедия",
            "Криминал", "Документальный", "Драма", "Семейный", "Фэнтези",
            "Нуар", "Исторический", "Ужасы", "Мюзикл", "Мистика",
            "Романтика", "Научная фантастика", "Короткометражный", "Спорт",
            "Триллер", "Война", "Вестерн", "Супергеройский", "Музыкальный",
            "Постапокалиптика", "Фантастика", "Сказка",
            "Политический", "Антиутопия", "Артхаус", "Комикс", "Шпионский",
            "Детектив"
        ]

        self.genre_checkboxes = {}
        for genre_name in genre_list:
            checkbox = QtWidgets.QCheckBox(genre_name)
            genre_input_layout.addWidget(checkbox)
            self.genre_checkboxes[genre_name] = checkbox

        for g in genre.split(", "):
            if g in self.genre_checkboxes:
                self.genre_checkboxes[g].setChecked(True)

        layout.addLayout(genre_input_layout)

        film_link_input = QtWidgets.QLineEdit(film_link)
        film_link_input.setPlaceholderText("Ссылка на фильм")
        film_link_input.setFixedHeight(40)
        film_link_input.setStyleSheet(
            "background-color: white; border: 1px solid #4169E1; border-radius: 5px; padding: 10px;")
        layout.addWidget(film_link_input)

        description_input = QtWidgets.QTextEdit(description)
        description_input.setPlaceholderText("Описание")
        layout.addWidget(description_input)

        save_button = QtWidgets.QPushButton("Сохранить изменения")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  
                color: white; 
                padding: 10px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                cursor: pointer;
            }
        """)
        save_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        save_button.clicked.connect(
            lambda: self.save_changes(title_input.text(), year_input.text(), rating_input.text(),
                                      self.get_selected_genres(),
                                      film_link_input.text(), poster_link, description_input.toPlainText(),
                                      edit_dialog, title))
        layout.addWidget(save_button)

        layout.addStretch()

        edit_dialog.exec()

    def get_selected_genres(self):
        selected_genres = []
        for genre_id, checkbox in self.genre_checkboxes.items():
            if checkbox.isChecked():
                selected_genres.append(genre_id)
        return selected_genres

    def add_genre(self, genre_name):
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO genres (name) VALUES (?)")
        query.addBindValue(genre_name)

        if query.exec():
            self.show_message("Успех", "Жанр успешно добавлен.", QtWidgets.QMessageBox.Icon.Information)
        else:
            self.show_message("Ошибка", f"Ошибка при добавлении жанра: {query.lastError().text()}",
                              QtWidgets.QMessageBox.Icon.Critical)

    def save_changes(self, title, year, rating, genre, film_link, poster_link, description, dialog, old_title):
        warning_message = "При изменении названия фильма может пропасть постер. Вы уверены, что хотите продолжить?"
        reply = QtWidgets.QMessageBox.warning(
            self,
            "Внимание",
            warning_message,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.No:
            return

        movie_id_query = QtSql.QSqlQuery()
        movie_id_query.prepare("SELECT id FROM movies WHERE title = ?")
        movie_id_query.addBindValue(old_title)
        movie_id_query.exec()

        movie_id = None
        if movie_id_query.next():
            movie_id = movie_id_query.value(0)

        if not movie_id:
            print("Movie ID not found!")
            return

        delete_genre_links_query = QtSql.QSqlQuery()
        delete_genre_links_query.prepare("DELETE FROM moviegenres WHERE movie_id = ?")
        delete_genre_links_query.addBindValue(movie_id)
        delete_genre_links_query.exec()

        for genre_name in genre:
            genre_id = self.get_genre_id(genre_name)
            if genre_id:
                self.link_movie_to_genre(movie_id, genre_id)

        genre_ids = ",".join(map(str, genre))

        query = QtSql.QSqlQuery()
        query.prepare(f"""
            UPDATE movies
            SET title = ?, year = ?, average_rating = ?, genres = ?, film_link = ?, poster_link = ?, description = ?
            WHERE title = ?
        """)
        query.addBindValue(title)
        query.addBindValue(year)
        query.addBindValue(rating)
        query.addBindValue(genre_ids)
        query.addBindValue(film_link)
        query.addBindValue(poster_link)
        query.addBindValue(description)
        query.addBindValue(old_title)

        if query.exec():
            dialog.accept()
            if hasattr(self.parent(), 'update_movie_table'):
                self.parent().update_movie_table()
        else:
            error_message = f"Ошибка при обновлении информации о фильме: {query.lastError().text()}"
            self.show_message("Ошибка", error_message, QtWidgets.QMessageBox.Icon.Critical)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def load_genres(self):
        query = QtSql.QSqlQuery("SELECT id, name FROM genres")
        genre_list = []
        while query.next():
            genre_id = query.value(0)
            genre_name = query.value(1)
            genre_list.append((genre_id, genre_name))
        return genre_list

    def create_genre_checkboxes(self):
        genre_list = self.load_genres()
        self.genre_checkboxes = {}

        genre_input_layout = QtWidgets.QVBoxLayout()
        for genre_id, genre_name in genre_list:
            checkbox = QtWidgets.QCheckBox(genre_name)
            genre_input_layout.addWidget(checkbox)
            self.genre_checkboxes[genre_id] = checkbox

        return genre_input_layout

    def create_button(self, text, bg_color, hover_color):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet(f"""
            padding: 12px; 
            background-color: {bg_color}; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.3s;
        """)
        button.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=2, yOffset=2))
        button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        button.setStyleSheet(f"""
            QPushButton {{
                padding: 12px; 
                background-color: {bg_color}; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 14px;
                font-weight: bold;
                transition: background-color 0.3s;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        return button

    def confirm_delete(self, title):
        message_box = QtWidgets.QMessageBox(self)
        message_box.setWindowTitle('Подтверждение удаления')
        message_box.setText(f'Вы действительно хотите удалить фильм "{title}"?')
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        yes_button = message_box.addButton('Да', QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        no_button = message_box.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.RejectRole)

        for button in [yes_button, no_button]:
            button.setFixedSize(100, 40)
            button.setStyleSheet("font-weight: bold;")

        message_box.exec()

        if message_box.clickedButton() == yes_button:
            self.delete_movie(title)

    def delete_movie(self, title):
        query = QtSql.QSqlQuery()
        query.prepare(f"DELETE FROM movies WHERE title = ?")
        query.addBindValue(title)

        if query.exec():
            self.show_message("Успех", "Фильм успешно удалён.", QtWidgets.QMessageBox.Icon.Information)
            self.close()
            if hasattr(self.parent(), 'update_movie_table'):
                self.parent().update_movie_table()
        else:
            self.show_message("Ошибка", "Ошибка при удалении фильма: " + query.lastError().text(),
                              QtWidgets.QMessageBox.Icon.Critical)

    def update_favorite_button(self, button, title):
        query = QtSql.QSqlQuery()
        query.prepare(f"SELECT favorite FROM movies WHERE title = ?")
        query.addBindValue(title)

        if query.exec() and query.next():
            is_favorite = query.value(0)
            if is_favorite:
                button.setText("Убрать из избранного")
            else:
                button.setText("Добавить в избранное")

    def toggle_favorites(self, title, button):
        query = QtSql.QSqlQuery()
        query.prepare(f"UPDATE movies SET favorite = NOT favorite WHERE title = ?")
        query.addBindValue(title)

        if query.exec():
            current_text = button.text()
            new_text = "Добавить в избранное" if current_text == "Убрать из избранного" else "Убрать из избранного"
            button.setText(new_text)
            message = "Фильм добавлен в избранное." if new_text == "Убрать из избранного" else "Фильм убран из избранного."
            self.show_message("Успех", message, QtWidgets.QMessageBox.Icon.Information)
        else:
            self.show_message("Ошибка", "Ошибка при обновлении избранного: " + query.lastError().text(),
                              QtWidgets.QMessageBox.Icon.Critical)

    def open_film_link(self, film_link):
        if film_link:
            QtGui.QDesktopServices.openUrl(QUrl(film_link))

    def show_message(self, title, message, icon):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()

class PersonalCabinet(QtWidgets.QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Личный кабинет")
        self.setGeometry(200, 200, 400, 300)
        self.username = username
        self.favorite_dialog = None
        self.movies_window = None

        self.setStyleSheet("background-color: #FFE4E1;")

        self.layout = QtWidgets.QVBoxLayout(self)
        top_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(top_layout)
        self.setWindowIcon(QtGui.QIcon(f'{icons}/personal_cabinet.png'))
        self.edit_profile_button = QtWidgets.QPushButton(self)
        edit_icon = QtGui.QIcon(f'{icons}/settings.png')
        self.edit_profile_button.setIcon(edit_icon)
        self.edit_profile_button.setIconSize(QtCore.QSize(30, 30))
        self.edit_profile_button.setFixedSize(50, 50)
        self.edit_profile_button.setStyleSheet("""
            QPushButton {
                border: none; 
                background-color: #FFDEAD;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FFA07A;
            }
        """)

        self.edit_profile_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        top_layout.addWidget(self.edit_profile_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.edit_profile_button.clicked.connect(self.open_edit_profile)

        self.exit_button = QtWidgets.QPushButton(self)
        exit_icon = QtGui.QIcon(f'{icons}/door.png')
        self.exit_button.setIcon(exit_icon)
        self.exit_button.setIconSize(QtCore.QSize(30, 30))
        self.exit_button.setFixedSize(50, 50)
        self.exit_button.setStyleSheet("""
            QPushButton {
                border: none; 
                background-color: #FFDEAD;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FFA07A;
            }
        """)

        self.exit_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        top_layout.addWidget(self.exit_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.exit_button.clicked.connect(self.confirm_logout)

        avatar_label = QtWidgets.QLabel(self)
        avatar_pixmap = QtGui.QPixmap(f'{icons}/avatar.jpeg')
        avatar_label.setPixmap(avatar_pixmap.scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        avatar_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(avatar_label)

        welcome_label = QtWidgets.QLabel(f"Добро пожаловать в систему, {username}!")
        welcome_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 18px; color: #333333;")
        self.layout.addWidget(welcome_label)

        self.favorite_button = QtWidgets.QPushButton("Избранное", self)
        self.layout.addWidget(self.favorite_button)
        self.movies_button = QtWidgets.QPushButton("Фильмы", self)
        self.layout.addWidget(self.movies_button)
        self.movie_selection_button = QtWidgets.QPushButton("Подбор фильмов", self)
        self.layout.addWidget(self.movie_selection_button)

        self.favorite_button.clicked.connect(self.open_favorites)
        self.movies_button.clicked.connect(self.open_movies)
        self.movie_selection_button.clicked.connect(self.open_movie_selection)

        self.setup_buttons()

    def setup_buttons(self):
        button_style = """
            QPushButton {
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        self.favorite_button.setStyleSheet(button_style)
        self.favorite_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.movies_button.setStyleSheet(button_style)
        self.movies_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        self.movie_selection_button.setStyleSheet(button_style)
        self.movie_selection_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

    def open_favorites(self):
        if self.favorite_dialog:
            self.favorite_dialog.hide()
        self.favorite_dialog = FavoritesDialog(username=self.username)
        self.favorite_dialog.show()

    def open_movies(self):
        if self.movies_window:
            self.movies_window.hide()
        self.movies_window = MainWindow(username=self.username)
        self.movies_window.show()

    def set_dark_theme(self, is_dark):
        self.dark_theme = is_dark
        self.apply_theme(is_dark)

    def open_movie_selection(self):
        movie_selection_dialog = MovieSelectionDialog(self.username, self)
        movie_selection_dialog.show()

    def open_edit_profile(self):
        edit_dialog = EditProfileDialog(self.username, self)
        edit_dialog.exec()

    def logout(self):
        self.hide()
        self.movies_window = MainWindow(username=self.username)
        self.favorite_dialog = FavoritesDialog(username=self.username)
        self.favorite_dialog.hide()
        self.movies_window.hide()
        self.open_login_window()

    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.exec()

    def confirm_logout(self):
        reply = QtWidgets.QMessageBox.question(
            self, 'Подтверждение выхода',
            'Вы хотите выйти из аккаунта?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.logout()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class EditProfileDialog(QtWidgets.QDialog):
    def __init__(self, username, personal_cabinet, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Редактировать профиль")
        self.setWindowIcon(QtGui.QIcon(f'{icons}/edit.png'))
        self.setGeometry(200, 200, 350, 250)
        self.personal_cabinet = personal_cabinet
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.name_input = QtWidgets.QLineEdit(self)
        self.name_input.setPlaceholderText("Имя")
        self.name_input.setFixedHeight(40)
        self.main_layout.addWidget(self.name_input)

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        self.username_input.setText(self.username)
        self.username_input.setReadOnly(True)
        self.username_input.mousePressEvent = self.show_username_edit_warning
        self.username_input.setFixedHeight(40)
        self.main_layout.addWidget(self.username_input)

        self.password_input = PasswordLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setFixedHeight(40)
        self.main_layout.addWidget(self.password_input)

        self.save_button = QtWidgets.QPushButton("Сохранить", self)
        self.save_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.main_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_changes)

        self.setStyleSheet(""" 
            QDialog {
                background-color: #FFE4E1;  
                border-radius: 10px; 
            }
            QLineEdit {
                padding: 10px; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                background-color: #ffffff;
            }
            QPushButton {
                padding: 10px; 
                background-color: #4CAF50; 
                color: white; 
                font-size: 14px; 
                border: none; 
                border-radius: 5px;
            }
        """)

        self.load_user_data()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def show_username_edit_warning(self, event):
        QtWidgets.QMessageBox.warning(self, "Ошибка", "Изменение имени пользователя запрещено.")

    def load_user_data(self):
        try:
            with open(users, newline='', encoding='utf-8') as csvfile:
                for line in csvfile:
                    name, user, pwd = line.strip().split('|')
                    if user == self.username:
                        self.name_input.setText(name)
                        return
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Пользователь не найден.")
        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Файл пользователей не найден.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def save_changes(self):
        try:
            lines = []
            user_found = False

            with open(users, 'r', encoding='utf-8') as csvfile:
                for line in csvfile:
                    name, user, pwd = line.strip().split('|')
                    if user == self.username:
                        hashed_password = self.hash_password(
                            self.password_input.text()) if self.password_input.text() else pwd
                        updated_name = self.name_input.text() if self.name_input.text() else name
                        lines.append(f"{updated_name}|{self.username_input.text()}|{hashed_password}\n")
                        user_found = True
                    else:
                        lines.append(line)

            if not user_found:
                raise ValueError("Пользователь не найден.")

            with open(users, 'w', encoding='utf-8') as csvfile:
                csvfile.writelines(lines)

            QtWidgets.QMessageBox.information(self, "Успех", "Данные успешно изменены.")
            self.hide()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))


class MovieSelectionDialog(QtWidgets.QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подбор фильмов по настроению")
        self.setWindowIcon(QtGui.QIcon(f'{icons}/selection.png'))
        self.setGeometry(300, 300, 400, 200)
        self.username = username
        self.setStyleSheet("background-color: #FFE4E1;")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        label = QtWidgets.QLabel("Выберите настроение для подбора фильма:")
        self.layout.addWidget(label)

        self.mood_combo = QtWidgets.QComboBox(self)
        self.mood_combo.addItems([
            "Хочется динамичных сцен",
            "Хочется драк и стрельбы",
            "Хочется пугаться",
            "Хочется поплакать",
            "Хочется фантастики",
            "Хочется военных действий",
            "Хочется посмотреть преступной деятельности",
            "Хочется приключений",
            "Хочется анимации",
            "Хочется биографии",
            "Хочется комедии",
            "Хочется документального",
            "Хочется семейного",
            "Хочется фэнтези",
            "Хочется исторического",
            "Хочется мистики",
            "Хочется романтики",
            "Хочется научной фантастики",
            "Хочется триллера",
            "Хочется вестерна",
            "Хочется супергеройского",
            "Хочется фантастики"
        ])
        self.layout.addWidget(self.mood_combo)

        self.select_button = QtWidgets.QPushButton("Подобрать фильм", self)
        self.layout.addWidget(self.select_button)

        self.select_button.clicked.connect(self.find_movie_by_genre)

    def find_movie_by_genre(self):
        mood_to_genre = {
            "Хочется динамичных сцен": "Экшн",
            "Хочется драк и стрельбы": "Боевик",
            "Хочется пугаться": "Ужасы",
            "Хочется поплакать": "Драма",
            "Хочется фантастики": "Сайфай",
            "Хочется военных действий": "Война",
            "Хочется посмотреть преступной деятельности": "Криминал",
            "Хочется приключений": "Приключения",
            "Хочется анимации": "Анимация",
            "Хочется биографии": "Биография",
            "Хочется комедии": "Комедия",
            "Хочется документального": "Документальный",
            "Хочется семейного": "Семейный",
            "Хочется фэнтези": "Фэнтези",
            "Хочется исторического": "Исторический",
            "Хочется мистики": "Мистика",
            "Хочется романтики": "Романтика",
            "Хочется научной фантастики": "Научная фантастика",
            "Хочется триллера": "Триллер",
            "Хочется вестерна": "Вестерн",
            "Хочется супергеройского": "Супергеройский",
            "Хочется фантастики": "Фантастика"
        }

        selected_mood = self.mood_combo.currentText()
        genre = mood_to_genre.get(selected_mood)

        if genre:
            self.open_movie_details(genre)

    def open_movie_details(self, genre):
        try:
            conn = sqlite3.connect(f'Database/Movies_{self.username}.db')
            cursor = conn.cursor()

            cursor.execute(""" 
                SELECT title, original_title, genres, average_rating, num_votes, year, film_link, description 
                FROM Movies 
                WHERE genres LIKE ?
            """, (f'%{genre}%',))
            movies = cursor.fetchall()

            if movies:

                movie_data = random.choice(movies)
                title, original_title, genres, average_rating, num_votes, year, film_link, description = movie_data

                poster_link = os.path.join(f"{posters}/{title}.jpeg")

                movie_details_window = FilmDetailsWindow(title, year, average_rating, film_link, poster_link,
                                                         description, genres, self.username)
                movie_details_window.show()
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", f"Фильмы с жанром {genre} не найдены.")

            conn.close()
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка подключения к базе данных: {e}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")


class AddMovieWindow(QtWidgets.QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowIcon(QtGui.QIcon(f'{icons}/add.png'))
        self.setWindowTitle("Добавить новый фильм")
        self.setGeometry(100, 100, 600, 600)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(15)

        self.setStyleSheet(""" 
            QDialog {
                background-color: #FFE4E1;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QLineEdit, QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QPushButton {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.selected_genres = []
        self.add_widgets()

    def add_widgets(self):
        self.title_label = QtWidgets.QLabel("Название:")
        self.layout.addWidget(self.title_label)
        self.title_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.title_input)

        self.original_title_label = QtWidgets.QLabel("Оригинальное название:")
        self.layout.addWidget(self.original_title_label)
        self.original_title_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.original_title_input)

        self.genre_label = QtWidgets.QLabel("Жанры:")
        self.layout.addWidget(self.genre_label)

        self.select_genres_button = QtWidgets.QPushButton("Выбрать жанры", self)
        self.select_genres_button.clicked.connect(self.open_genre_selection)
        self.layout.addWidget(self.select_genres_button)

        self.selected_genres_label = QtWidgets.QLabel("Выбранные жанры: None", self)
        self.layout.addWidget(self.selected_genres_label)

        self.average_rating_label = QtWidgets.QLabel("Рейтинг:")
        self.layout.addWidget(self.average_rating_label)
        self.average_rating_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.average_rating_input)

        self.num_votes_label = QtWidgets.QLabel("Количество голосов:")
        self.layout.addWidget(self.num_votes_label)
        self.num_votes_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.num_votes_input)

        self.year_label = QtWidgets.QLabel("Год:")
        self.layout.addWidget(self.year_label)
        self.year_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.year_input)

        self.film_link_label = QtWidgets.QLabel("Ссылка на фильм:")
        self.layout.addWidget(self.film_link_label)
        self.film_link_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.film_link_input)

        self.description_label = QtWidgets.QLabel("Описание:")
        self.layout.addWidget(self.description_label)
        self.description_input = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.description_input)

        self.add_button = QtWidgets.QPushButton("Добавить фильм", self)
        self.add_button.clicked.connect(self.add_movie_to_db)
        self.layout.addWidget(self.add_button)

    def open_genre_selection(self):
        genre_window = SelectGenreWindow(self)
        if genre_window.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.selected_genres = genre_window.get_selected_genres()

            if self.selected_genres:
                self.selected_genres_label.setText(f"Выбранные жанры: {', '.join(self.selected_genres)}")
            else:
                self.selected_genres_label.setText("Выбранные жанры: None")

    def add_movie_to_db(self):
        title = self.title_input.text() or "Информация отсутствует"
        original_title = self.original_title_input.text() or "Информация отсутствует"
        average_rating = self.average_rating_input.text() or "Информация отсутствует"
        num_votes = self.num_votes_input.text() or "Информация отсутствует"
        year = self.year_input.text() or "Информация отсутствует"
        film_link = self.film_link_input.text() or "Информация отсутствует"
        description = self.description_input.toPlainText() or "Информация отсутствует"

        query = QtSql.QSqlQuery()

        sql_movie = """
            INSERT INTO movies (title, original_title, average_rating, num_votes, year, film_link, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        query.prepare(sql_movie)
        query.addBindValue(title)
        query.addBindValue(original_title)
        query.addBindValue(average_rating)
        query.addBindValue(num_votes)
        query.addBindValue(year)
        query.addBindValue(film_link)
        query.addBindValue(description)

        if not query.exec():
            print(f"Error adding movie: {query.lastError().text()}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить фильм: {query.lastError().text()}")
            return

        movie_id = query.lastInsertId()
        print(f"Added movie with ID: {movie_id}")

        genres_str = ", ".join(self.selected_genres)
        update_query = QtSql.QSqlQuery()
        update_query.prepare("UPDATE movies SET genres = ? WHERE id = ?")
        update_query.addBindValue(genres_str)
        update_query.addBindValue(movie_id)

        if not update_query.exec():
            print(f"Error updating genres for movie {movie_id}: {update_query.lastError().text()}")

        for genre_name in self.selected_genres:
            genre_id = self.get_genre_id(genre_name)
            if not genre_id:
                genre_id = self.add_genre(genre_name)
                print(f"Added genre '{genre_name}' with ID: {genre_id}")

            if genre_id:
                self.link_movie_to_genre(movie_id, genre_id)

        QMessageBox.information(self, "Успех", "Фильм успешно добавлен!")
        self.hide()

    def add_genre(self, genre_name):
        if not genre_name:
            print("Genre name is empty.")
            return None

        existing_genre_id = self.get_genre_id(genre_name)
        if existing_genre_id:
            print(f"Genre '{genre_name}' already exists with ID: {existing_genre_id}")
            return existing_genre_id

        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO genres (name) VALUES (?)")
        query.addBindValue(genre_name.strip())

        if query.exec():
            genre_id = query.lastInsertId()
            print(f"Genre '{genre_name}' inserted with ID: {genre_id}")
            return genre_id
        else:
            print(f"Error adding genre '{genre_name}': {query.lastError().text()}")
            return None

    def get_genre_id(self, genre_name):
        query = QtSql.QSqlQuery()
        query.prepare("SELECT id FROM genres WHERE name = ?")
        query.addBindValue(genre_name)
        query.exec()

        if query.next():
            return query.value(0)
        else:
            print(f"Genre '{genre_name}' not found.")
        return None

    def link_movie_to_genre(self, movie_id, genre_id):
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO moviegenres (movie_id, genre_id) VALUES (?, ?)")
        query.addBindValue(movie_id)
        query.addBindValue(genre_id)

        if not query.exec():
            print(f"Error linking movie {movie_id} to genre {genre_id}: {query.lastError().text()}")

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class SelectGenreWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите жанры")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setWindowIcon(QtGui.QIcon(f'{icons}/selection.png'))

        self.genre_list_widget = QtWidgets.QListWidget(self)
        self.genre_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        genres = [
            "Экшн", "Приключения", "Анимация", "Биография", "Комедия",
            "Криминал", "Документальный", "Драма", "Семейный", "Фэнтези",
            "Нуар", "Исторический", "Ужасы", "Мюзикл", "Мистика",
            "Романтика", "Научная фантастика", "Короткометражный", "Спорт",
            "Триллер", "Война", "Вестерн", "Супергеройский", "Музыкальный",
            "Постапокалиптика", "Фантастика", "Сказка",
            "Политический", "Антиутопия", "Артхаус", "Комикс", "Шпионский",
            "Детектив"
        ]

        self.genre_list_widget.addItems(genres)
        self.layout.addWidget(self.genre_list_widget)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.cancel_button = QtWidgets.QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)

    def get_selected_genres(self):
        selected_items = self.genre_list_widget.selectedItems()
        selected_genres = [item.text() for item in selected_items]
        return selected_genres


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
