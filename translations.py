translation_strings = {
    'first_msg': {'ru': '''Добро пожаловать в VKSuicide!\nДанная программа поможет вам удалить следы вашего присутствия во ВКонтакте!''',
                  'en': '''Welcome to VKSuicide!\nThis tool can help you to remove traces of your presence on VKontakte!'''},
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
    'enter_token': {'ru': '''Введите токен, токен можно взять здесь: https://vkhost.github.io/ \nВ настройках выделите все пункты''',
                     'en': '''Enter access token, you can get token here: https://vkhost.github.io/ \nIn settings select all positions'''},
    'invalid_token': {'ru': '''Недействительный токен''',
                      'en': '''Invalid token'''},
    'select_for_deletion': {'ru': '''Введите то, что нужно удалить в одной строке через пробел:\n
    [1] Лайки\n
    [2] Комментарии\n
    [3] Стена\n
    [4] Фотографии в сообщениях(Медленно)\n
    [5] Фотографии в альбомах
    ''',
                            'en': '''Enter what you want to delete in one line separated by a space:\n
    [1] Likes\n
    [2] Comments\n
    [3] Wall\n
    [4] Photos in messages(Slow)\n
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
    'archive_messages_parsing': {
        'ru': '''Обработка архива...''',
        'en': '''Archive parsing...'''
    },
    'getting_list_of_msg': {
        'ru': '''Получение списка сообщений...''',
        'en': '''Receiving messages list...'''
    },
    'done': {
        'ru': '''Работа завершена''',
        'en': '''Done'''
    }
}


def get_string(string_name: str, lang: str) -> str:
    return translation_strings.get(string_name, {}).get(lang, 'error')
