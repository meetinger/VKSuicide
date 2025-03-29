translation_strings = {
    'choose_language': {'ru': '''Выберите язык (Введите ru или en)''',
                        'en': '''Choose language (Enter ru or en)'''},
    'first_msg': {'ru': '''Добро пожаловать в VKSuicide!\nДанная программа поможет вам удалить следы вашего присутствия во ВКонтакте!''',
                  'en': '''Welcome to VKSuicide!\nThis tool can help you to remove traces of your presence on VKontakte!'''},
    'captcha_solver_detected': {'ru': '''Модуль распознавания капчи обнаружен!''',
                                'en': '''Captcha solver detected!'''},
    'captcha_solver_not_found': {'ru': '''Модуль распознавания капчи не обнаружен! Продолжить? (Введите yes или no)''',
                                 'en': '''Captcha solver not detected! (Enter yes or no)'''},
    'zip_archive_detected': {'ru': '''Обнаружен архив, Вы хотите его распаковать? (Введите yes или no)''',
                             'en': '''Archive detected, do you want unzip it? (Enter yes or no)'''
                             },
    'unzipping_archive': {'ru': '''Распаковка архива''',
                          'en': '''Unzipping archive'''},
    'unzipping_done': {'ru': '''Распаковка завершена''',
                       'en': '''Unzipping done'''},
    'dir_archive_detected': {'ru': '''Обнаружен распакованный архив''',
                             'en': '''Unzipped archive detected'''},
    'dir_archive_not_detected': {'ru': '''Архив не обнаружен. Убедитесь, что вы скопировали его в папку с программой''',
                                 'en': '''The archive was not found. Make sure you have copied it to the program folder'''},
    'auth_type': {'ru': '''Выберите тип авторизации(введите 1 или 2):\n
[1] Логин/Пароль
[2] Токен
    ''',
                  'en': '''Select authorization type(enter 1 or 2):\n
[1] Login/Password
[2] Token
                  '''},
    'enter_login': {'ru': '''Введите логин''',
              'en': '''Enter login'''},
    'enter_password': {'ru': '''Введите пароль''',
                 'en': '''Enter password'''},
    'enter_2fa': {
        'ru': '''Введите код 2FA''',
        'en': '''Enter 2FA code'''
    },
    'enter_token': {'ru': '''Введите токен(или ссылку с токеном).\nP.S: токен можно взять здесь: https://vkhost.github.io/ На странице выберите vk.com и предоставьте доступ''',
                     'en': '''Enter access token(or link with token).\nP.S: you can get token here: https://vkhost.github.io/ On the page select vk.com'''},
    'invalid_token': {'ru': '''Недействительный токен''',
                      'en': '''Invalid token'''},
    'select_for_deletion': {'ru': '''Введите то, что нужно удалить в одной строке через пробел:\n
[1] Лайки
[2] Комментарии
[3] Стена
[4] Фотографии в сообщениях(Медленно)
[5] Фотографии в альбомах
    ''',
                            'en': '''Enter what you want to delete in one line separated by a space:\n
[1] Likes
[2] Comments
[3] Wall
[4] Photos in messages(Slow)
[5] Photos in albums
                            '''},
    'error': {
        'ru': 'Ошибка',
        'en': 'Error'
    },
    'success': {
        'ru': '''Успешно''',
        'en': '''Success'''
    },
    'deleting': {
        'ru': '''Удаление''',
        'en': '''Deleting'''
    },
    'err14': {
        'ru': '''Капча, ждём перед следующей попыткой''',
        'en': '''Captcha, waiting before next attempt'''
    },
    'err14_solver': {
        'ru': '''Капча, решаем...''',
        'en': '''Captcha, solving...'''
    },
    'attempt_limit': {
        'ru': '''Достигнут лимит попыток, переход на следующую задачу''',
        'en': '''The limit of attempts has been reached, moving to the next task'''
    },
    'deleting_likes': {
        'ru': '''Удаление лайков''',
        'en': '''Likes deleting'''
    },
    'deleting_comments': {
        'ru': '''Удаление комментариев''',
        'en': '''Comments deleting'''
    },
    'deleting_wall': {
        'ru': '''Удаление стены''',
        'en': '''Wall deleting'''
    },
    'deleting_photos_in_messages': {
        'ru': '''Удаление фотографий в сообщениях''',
        'en': '''Deleting photos in messages'''
    },
    'deleting_photos_in_albums': {
        'ru': '''Удаление фотографий в альбомах''',
        'en': '''Deleting photos in albums'''
    },
    'likes_files_not_found': {
        'ru': '''Файлы лайков не обнаружены''',
        'en': '''Likes files not found'''
    },
    'comments_files_not_found': {
        'ru': '''Файлы комментариев не обнаружены''',
        'en': '''Comments files not found''',
    },
    'wall_files_not_found': {
        'ru': '''Файлы стены не обнаружены''',
        'en': '''Wall files not found'''
    },
    'photos_in_albums_files_not_found': {
        'ru': '''Файлы фотографий в альбомах не обнаружены''',
        'en': '''Photos in albums files not found'''
    },
    'photos_in_messages_files_not_found': {
        'ru': '''Файлы фотографий в сообщениях не обнаружены''',
        'en': '''Photos in messages files not found'''
    },

    'likes_deleted': {
        'ru': '''Лайки удалены''',
        'en': '''Likes deleted'''
    },
    'comments_deleted': {
        'ru': '''Комментарии удалены''',
        'en': '''Comments deleted'''
    },
    'wall_deleted': {
        'ru': '''Стена удалена''',
        'en': '''Wall deleted'''
    },
    'photos_in_albums_deleted': {
        'ru': '''Фотографии в альбомах удалены''',
        'en': '''Photos in albums deleted'''
    },
    'photos_in_messages_deleted': {
        'ru': '''Фотографии в сообщениях удалены''',
        'en': '''Photos in messages deleted'''
    },
    'err9': {
        'ru': '''Ограничение кол-ва запросов, ждём...''',
        'en': '''Requests limit, waiting...'''
    },
    'done': {
        'ru': '''Работа завершена''',
        'en': '''Done'''
    }
}


def get_string(string_name: str, lang: str) -> str:
    return translation_strings.get(string_name, {}).get(lang, 'error')
