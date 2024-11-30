# Проект "Умный подбор и поиск фильмов"

## Дисклеймер

### Внимание!

**Данное приложение предоставляет информацию о фильмах** на основании данных, полученных из различных источников. Несмотря на усилия по обеспечению точности и актуальности информации, я не могу гарантировать её полную достоверность.

Пожалуйста, учитывайте, что данные о фильмах, такие как рейтинги, годы выпуска, описание и другие параметры, могут быть неверными или устаревшими. Я настоятельно рекомендую проверять информацию из официальных источников перед принятием каких-либо решений, основанных на данных, представленных в приложении.

Используя данное приложение, вы соглашаетесь с тем, что я **не несу ответственности** за любые последствия, связанные с использованием недостоверной информации.

## Описание

Проект "Умный подбор и поиск фильмов" представляет собой приложение для работы с базой данных фильмов. Пользователи могут искать фильмы, просматривать их детали и получать доступ к постерам и описаниям. Приложение имеет интуитивно понятный интерфейс и позволяет легко взаимодействовать с данными.

## Установка

1. Убедитесь, что у вас установлен Python (версия 3.6 и выше).
2. Клонируйте репозиторий или скачайте архив с проектом.
3. Установите необходимые зависимости с помощью pip:

   ```bash
   pip install -r requirements.txt


# Структура проекта

- `main.py` - основной файл приложения.
- `config.py` - Файл с путями
- `Database/` - папка, содержащая базу данных фильмов.
- `posters/` - папка с постерами фильмов.
- `icons/` - папка с иконками

# Используемые технологии

- **PyQt6** — библиотека для создания графических интерфейсов.
- **SQLite** — легковесная база данных для хранения информации о фильмах.
- **Pandas** — библиотека для анализа и обработки табличных данных 
- **Hashlib** — библиотека для хэширования данных, например, паролей или уникальных идентификаторов.



# Как использовать

1. **Запустите приложение.**
   - Дважды щелкните на иконку приложения, чтобы открыть его.

2. **Поиск фильма.**
   - Введите название фильма в поле поиска. Это позволит отфильтровать результаты и быстро найти нужный фильм.

3. **Просмотр информации о фильме.**
   - Дважды щелкните на нужном фильме из списка результатов, чтобы открыть окно с подробной информацией о фильме.

4. **Добавление в избранное.**
   - Если вы хотите сохранить фильм в избранном, нажмите кнопку "Добавить в избранное" на странице с информацией о фильме.

5. **Просмотр избранных фильмов.**
   - Перейдите в раздел "Избранное" через меню, чтобы увидеть все сохраненные фильмы.

6. **Регистрация и вход.**
   - Если вы еще не зарегистрированы, нажмите кнопку "Регистрация" на экране входа. Введите необходимые данные и подтвердите регистрацию.
   - Для входа в приложение введите ваше имя пользователя и пароль, затем нажмите "Войти".

7. **Выход из приложения.**
   - Чтобы выйти из приложения, нажмите кнопку "Выход" в меню. Приложение закроется, и вы вернетесь на экран входа.


# Проблемы и решения

- Если приложение не запускается, убедитесь, что все зависимости установлены и база данных доступна.
- Если вы не видите постеры, проверьте правильность указанных путей к файлам изображений.


# Проблемы и решения

- **Приложение не запускается.**
  - Убедитесь, что все зависимости установлены и база данных доступна.
  - Проверьте наличие необходимых библиотек, указанных в файле `requirements.txt`.

- **Не видите постеры.**
  - Проверьте правильность указанных путей к файлам изображений.
  - Убедитесь, что изображения действительно находятся по указанным путям и имеют правильные расширения (например, .png, .jpg).

- **Ошибка при входе в приложение.**
  - Убедитесь, что введенные имя пользователя и пароль соответствуют данным в базе пользователей.
  - Проверьте наличие пробелов или опечаток в введенных данных.

- **Не отображается информация о фильмах.**
  - Убедитесь, что база данных фильмов правильно настроена и содержит данные.
  - Проверьте, что приложение имеет доступ к базе данных.

- **Проблемы с отображением интерфейса.**
  - Убедитесь, что вы используете последнюю версию PyQt.
  - Проверьте настройки графического интерфейса, такие как масштабирование или разрешение экрана.

- **Не удается добавить фильм в избранное.**
  - Проверьте, что у вас есть необходимые права доступа для записи в базу данных.
  - Убедитесь, что фильм выбран корректно перед попыткой добавления в избранное.

- **Приложение зависает или работает медленно.**
  - Проверьте, достаточно ли ресурсов на вашем компьютере (оперативная память, процессор).
  - Закройте другие неиспользуемые приложения для освобождения ресурсов.

- **Общие ошибки.**
  - Попробуйте перезапустить приложение или компьютер.
## Документация

- [Документация по PyQt](https://doc.qt.io/qtforpython/)
- [Документация по SQLite](https://www.sqlite.org/docs.html)

