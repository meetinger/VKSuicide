import datetime
import random
import re
import sys
import time
import codecs

from GlobalVars import GlobalVars
from VKApi import VKApi
from inputs import *
from translations import get_string

import os

import zipfile

from utils import progress_bar, clear_last_line
from workers import getMsgWorker


GlobalVars.language = getArgs(numOfArgs=1, allowedArgs=['ru', 'en'], startMsg='Choose Language: ru, en', argType=str)[0]

print(get_string('first_msg', GlobalVars.language))

captcha_solver = True

try:
    import vk_captchasolver as vc
except ImportError as e:
    captcha_solver = False

if captcha_solver:
    print(get_string('captcha_solver_detected', GlobalVars.language))
else:
    print(get_string('captcha_solver_not_found', GlobalVars.language))

cur_dir_list = os.listdir()

if 'Archive.zip' in cur_dir_list:
    ans = \
        getArgs(numOfArgs=1, allowedArgs=['yes', 'no'], startMsg=get_string('zip_archive_detected', GlobalVars.language),
                argType=str)[0]
    if ans == "yes":
        print(get_string('unzipping_archive', GlobalVars.language))
        archive = zipfile.ZipFile('Archive.zip', 'r')
        archive.extractall('Archive')
        print(get_string('unzipping_done', GlobalVars.language))

cur_dir_list = os.listdir()

if 'Archive' in cur_dir_list:
    print(get_string('dir_archive_detected', GlobalVars.language))
else:
    print(get_string('dir_archive_not_detected', GlobalVars.language))
    sys.exit()

access_token = getArgsInline(numOfArgs=1, allowedArgs=lambda token: VKApi.check_token(token).get('response', -1) > 0,
                             startMsg=get_string('enter_token', GlobalVars.language), argType=str,
                             errMsg=get_string('invalid_token', GlobalVars.language))[0]

vk_api = VKApi(access_token)

user_id = vk_api.execute_method('users.get', {})['response'][0]['id']

# token_valid = (VKApi.check_token(token).get('response', -1) > 0)
#
# while not token_valid:
#     print('')

available_for_deletion = {1: "likes",
                          2: "comments",
                          3: "wall",
                          4: 'photos_in_messages',
                          5: 'photos_in_albums'}

to_delete = getArgsInline(numOfArgs=-1, allowedArgs=list(range(1, 10)),
                          startMsg=get_string('select_for_deletion', GlobalVars.language), argType=int)

to_delete_str_arr = [available_for_deletion.get(i, -1) for i in to_delete]

archive_dir_list = os.listdir('Archive')

log_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'

if not os.path.exists('logs/'):
    os.makedirs('logs/')

log_file = codecs.open('logs/' + log_file_name, 'a', "utf-8")


def build_log_str(res, link, log_file, additional='', print_log=True):
    log_string = '[{}] {} '.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), link)

    if 'error' in res:
        log_string += get_string('error', GlobalVars.language) + " " + str(res['error'].get('error_code', '')) + " " + \
                      res['error'].get('error_msg', '')
        if res['error'].get('error_code', '') == 14:
            log_string += " | " + (get_string('err14_solver', GlobalVars.language) if captcha_solver else get_string('err14', GlobalVars.language))
        if res['error'].get('error_code', '') == 9:
            log_string += " | " + get_string('err9', GlobalVars.language)
    else:
        log_string += get_string('success', GlobalVars.language)
    log_string += additional
    if print_log:
        print(log_string)
    log_file.write(log_string + '\n')


delays = {'normal': (1, 5), 'captcha': (1, 2)}
attempts_limit = 5

parameters_for_deleting = {key: [] for key in to_delete_str_arr}

if 'likes' in to_delete_str_arr:
    # print(get_string('deleting_likes', language))
    # log_file.write(get_string('deleting_likes', language) + '\n')
    likes_dir_list = os.listdir('Archive/likes')
    likes_dir_list = [i for i in likes_dir_list if os.path.isdir('Archive/likes/' + i)]
    progress_counter = 0
    for cur_dir_name in likes_dir_list:
        likes_files = os.listdir('Archive/likes/' + cur_dir_name)
        for cur_file_name in likes_files:
            cur_file = open('Archive/likes/' + cur_dir_name + '/' + cur_file_name, 'r')
            lines = cur_file.readlines()

            text = ''.join(lines)

            content_type, *modificator = cur_dir_name.split('_')

            link_regex = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+'

            if modificator:
                link_regex = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+\?\w+\=[-0-9]+'

            matches = re.findall(link_regex, text)

            for match in matches:
                owner_id = re.search(r'[-0-9]+', match).group()

                item_regex = r'_[-0-9]+'

                if modificator:
                    item_regex = r'\?\w+\=[-0-9]+'

                item_id = re.sub('[^0-9]', '', re.search(item_regex, match).group())

                parameters_for_deleting['likes'].append({'link': match, 'method': 'likes.delete',
                                                         'params': {'type': content_type, 'owner_id': int(owner_id),
                                                                    'item_id': int(item_id)}})
            progress_counter = progress_counter + 1/len(likes_files)
            progress_bar(50, progress_counter, len(likes_dir_list), additional_str=get_string('archive_likes_parsing', GlobalVars.language))

    progress_bar(50, 1, 1, additional_str=get_string('archive_likes_parsing', GlobalVars.language)+f' ({len(parameters_for_deleting["likes"])})')


if 'comments' in to_delete_str_arr:
    print()
    comments_file_list = os.listdir('Archive/comments')
    progress_counter = 0
    for cur_file_name in comments_file_list:
        cur_file = open('Archive/comments/' + cur_file_name, 'r')
        lines = cur_file.readlines()

        text = ''.join(lines)

        link_regex = r'https://vk.com/[a-z]+[-0-9]+_[0-9]+\?\w+\=[-0-9]+\&*\w*\=*[-0-9]*'

        matches = list(set(re.findall(link_regex, text)))

        for match in matches:
            owner_id = re.search(r'[-0-9]+', match).group()
            reply_id = re.search(r'reply=[-0-9]+', match).group()
            thread_id = re.search(r'thread=[-0-9]+', match)
            comment_id = reply_id
            if thread_id is not None:
                thread_id = thread_id.group()
                comment_id = thread_id

            comment_id = re.sub('[^0-9]', '', comment_id)

            parameters_for_deleting['comments'].append({'link': match, 'method': 'wall.deleteComment',
                                                        'params': {'owner_id': int(owner_id),
                                                                   'comment_id': int(comment_id)}})
            progress_counter = progress_counter + 1/len(matches)
            progress_bar(50, progress_counter, len(comments_file_list),
                         additional_str=get_string('archive_comments_parsing', GlobalVars.language))

    progress_bar(50, 1, 1, additional_str=get_string('archive_comments_parsing',
                                                     GlobalVars.language) + f' ({len(parameters_for_deleting["comments"])})')

if 'wall' in to_delete_str_arr:
    print()
    # print(get_string('deleting_wall', language))
    # log_file.write(get_string('deleting_wall', language) + '\n')
    wall_files = os.listdir('Archive/wall')
    wall_files = [i for i in wall_files if not os.path.isdir('Archive/wall/' + i)]
    progress_counter = 0
    for cur_file_name in wall_files:
        cur_file = open('Archive/wall/' + cur_file_name, 'r')
        lines = cur_file.readlines()

        text = ''.join(lines)

        matches = list(set(re.findall(r'https://vk.com/wall[-0-9]+_[0-9]+', text)))

        for match in matches:
            owner_id = re.search('[-0-9]+', match).group()
            post_id = re.sub('[^0-9]', '', re.search('_[-0-9]+', match).group())

            parameters_for_deleting['wall'].append({'link': match, 'method': 'wall.delete',
                                                    'params': {'owner_id': int(owner_id), 'post_id': int(post_id)}})
            progress_counter = progress_counter + 1/len(matches)

            progress_bar(50, progress_counter, len(wall_files),
                         additional_str=get_string('archive_wall_parsing', GlobalVars.language))
    progress_bar(50, 1, 1, additional_str=get_string('archive_wall_parsing',
                                                     GlobalVars.language) + f' ({len(parameters_for_deleting["wall"])})')

get_msg_threads_num = 15
if 'photos_in_messages' in to_delete_str_arr:
    print()
    # print(get_string('archive_messages_parsing', GlobalVars.language))
    msg_dirs = os.listdir('Archive/messages')
    msg_dirs = [i for i in msg_dirs if os.path.isdir('Archive/messages/' + i)]

    msgs_id = []

    progress_counter = 0
    for cur_msg_dir in msg_dirs:
        # res = vk_api.execute_method('messages.getHistoryAttachments', {'peer_id':cur_msg_dir, 'media_type': 'photo', 'count': 200})
        # print(res)

        msg_files = os.listdir('Archive/messages/' + cur_msg_dir)
        for cur_file_name in msg_files:
            # print('Archive/messages/' + cur_msg_dir + '/' + cur_file_name)
            cur_file = open('Archive/messages/' + cur_msg_dir + '/' + cur_file_name, 'r')
            lines = cur_file.readlines()

            text = ''.join(lines)

            matches = re.findall(r'<div class="message".*?<div class="attachment">.*?</div>', text, re.DOTALL)

            for match in matches:
                msgs_id.append(re.sub('[^0-9]', '', re.search(r'data-id="\d*"', match).group()))
            progress_counter = progress_counter + 1/len(msg_files)
            progress_bar(50, progress_counter, len(msg_dirs), additional_str=get_string('archive_messages_parsing', GlobalVars.language))

    progress_bar(50, 1, 1, additional_str=get_string('archive_messages_parsing',
                                                     GlobalVars.language) + f' ({len(msgs_id)})')
    print()

    msgs_id_batches = [msgs_id[(i - 1) * 100:i * 100] for i in range(1, int(len(msgs_id) / 100) + 2)]
    get_msg_threads = []

    for i in range(1, int(len(msgs_id_batches) / get_msg_threads_num) + 2):
        tmp = getMsgWorker(vk_api, msgs_id_batches[(i-1) * get_msg_threads_num:i * get_msg_threads_num], len(msgs_id_batches))
        get_msg_threads.append(tmp)
        tmp.start()

    [thread.join() for thread in get_msg_threads]

    progress_bar(50, 1, 1, additional_str=get_string('getting_list_of_msg',
                                                     GlobalVars.language) + f' ({len(GlobalVars.msgs)})')

    def filter_func(msg):
        for attachment in msg['attachments']:
            if attachment['type'] == 'photo' and attachment['photo']['owner_id'] == user_id:
                return True
        return False


    msgs = list(filter(filter_func, GlobalVars.msgs))

    print()
    print(get_string('msgs_found', GlobalVars.language).format(len(msgs)))

    for msg in msgs:
        for attachment in msg['attachments']:
            if attachment['type'] == 'photo':
                photo = attachment['photo']
                parameters_for_deleting['photos_in_messages'].append(
                    {'link': 'Owner-id: {} Photo-id: {}'.format(photo['owner_id'], photo['id']),
                     'method': 'photos.delete',
                     'params': {'owner_id': photo['owner_id'],
                                'photo_id': photo['id']}})

    print(get_string('photos_found', GlobalVars.language).format(len(parameters_for_deleting['photos_in_messages'])), end='\r')

if 'photos_in_albums' in to_delete_str_arr:
    print()
    progress_counter = 0
    albums = os.listdir('Archive/photos/photo-albums')
    for album in albums:
        file = open('Archive/photos/photo-albums/' + album)
        lines = file.readlines()
        text = ''.join(lines)

        photos_links = list(set(re.findall(r'https://vk.com/photo\d+_\d+', text)))

        for link in photos_links:
            finded = re.findall(r'\d+', link)
            owner_id = finded[0]
            photo_id = finded[1]
            parameters_for_deleting['photos_in_albums'].append({'link': link, 'method': 'photos.delete',
                                                                'params': {'owner_id': owner_id,
                                                                           'photo_id': photo_id}})
        progress_counter = progress_counter + 1

        progress_bar(50, progress_counter, len(albums),
                         additional_str=get_string('photos_in_albums_parsing', GlobalVars.language))

    progress_bar(50, 1, 1, additional_str=get_string('photos_in_albums_parsing',
                                                     GlobalVars.language) + f' ({len(parameters_for_deleting["photos_in_albums"])})')

indexes = {key: 0 for key in to_delete_str_arr}

print()

while True:
    done = True
    for key in parameters_for_deleting.keys():
        clear_last_line()
        print("Deleting", key, sep=' ')
        log_file.write('Deleting ' + key + '\n')
        for i in range(indexes[key], len(parameters_for_deleting[key])):
            time.sleep(random.randint(delays['normal'][0], delays['normal'][1]) if not captcha_solver else 0)

            line = parameters_for_deleting[key][i]

            res = vk_api.execute_method(line['method'], line['params'])

            clear_last_line()

            build_log_str(res=res, link=line['link'], log_file=log_file)

            fail_counter = 1
            progress_bar(50, i, len(parameters_for_deleting[key])-1, additional_str='Deleting ' + key)
            # print()
            while res.get('error', {'error_code': 0}).get('error_code', 0) == 14 or res.get('error', {'error_code': 0}).get('error_code', 0) == 9:
                if captcha_solver and res.get('error', {'error_code': 0}).get('error_code', 0) == 14:
                    captcha_sid = res['error']['captcha_sid']
                    captcha_key = vc.solve(sid=captcha_sid, s=1)

                    line['params'].update({'captcha_sid': captcha_sid, 'captcha_key': captcha_key})

                    res = vk_api.execute_method(line['method'], line['params'])

                    clear_last_line()
                    build_log_str(res=res, link=line['link'], log_file=log_file)
                else:
                    time.sleep(random.randint(delays['captcha'][0], delays['captcha'][1]))

                    fail_counter = fail_counter + 1
                    clear_last_line()

                    res = vk_api.execute_method(line['method'], line['params'])

                    build_log_str(res=res, link=line['link'], log_file=log_file,
                                  additional=" | " + get_string('attempt_limit',
                                                                GlobalVars.language) if fail_counter >= attempts_limit else '')

                progress_bar(50, i, len(parameters_for_deleting[key])-1, additional_str='Deleting ' + key)
                if fail_counter >= attempts_limit:
                    break

            indexes[key] = indexes[key] + 1

            if fail_counter >= attempts_limit:
                indexes[key] = indexes[key] - 1
                break

    for key in parameters_for_deleting.keys():
        if indexes[key] < len(parameters_for_deleting[key]) - 1:
            done = False

    if done:
        break

print()
print(get_string('done', GlobalVars.language))
log_file.write(get_string('done', GlobalVars.language) + '\n')
log_file.close()
