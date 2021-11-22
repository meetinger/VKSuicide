import datetime
import random
import time
import codecs

from HTMLDocument import HTMLDocument
from VKApi import VKApi
from inputs import *
from translations import get_string

import os

import zipfile

language = getArgs(numOfArgs=1, allowedArgs=['ru', 'en'], startMsg='Choose Language: ru, en', argType=str)[0]

print(get_string('first_msg', language))

cur_dir_list = os.listdir()

if 'Archive.zip' in cur_dir_list:
    ans = \
        getArgs(numOfArgs=1, allowedArgs=['yes', 'no'], startMsg=get_string('zip_archive_detected', language),
                argType=str)[
            0]
    if ans == "yes":
        print(get_string('unzipping_archive', language))
        archive = zipfile.ZipFile('Archive.zip', 'r')
        archive.extractall('Archive')
        print(get_string('unzipping_done', language))

cur_dir_list = os.listdir()

if 'Archive' in cur_dir_list:
    print(get_string('dir_archive_detected', language))

access_token = getArgsInline(numOfArgs=1, allowedArgs=lambda token: VKApi.check_token(token).get('response', -1) > 0,
                             startMsg=get_string('enter_token', language), argType=str,
                             errMsg=get_string('invalid_token', language))[0]

vk_api = VKApi(access_token)

user_id = vk_api.execute_method('users.get', {})['response'][0]['id']

# token_valid = (VKApi.check_token(token).get('response', -1) > 0)
#
# while not token_valid:
#     print('')

available_for_deletion = {1: "likes",
                          2: "comments",
                          3: "wall",
                          4: 'photos_in_messages'}

to_delete = getArgsInline(numOfArgs=-1, allowedArgs=list(range(1, 10)),
                          startMsg=get_string('select_for_deletion', language), argType=int)

to_delete_str_arr = [available_for_deletion.get(i, -1) for i in to_delete]

archive_dir_list = os.listdir('Archive')

log_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'

if not os.path.exists('logs/'):
    os.makedirs('logs/')

log_file = codecs.open('logs/' + log_file_name, 'a', "utf-8")


def build_log_str(res, link, log_file, additional=''):
    log_string = '[{}] {} '.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), link)

    if 'error' in res:
        log_string += get_string('error', language) + " " + str(res['error'].get('error_code', '')) + " " + \
                      res['error'].get('error_msg', '')
        if res['error'].get('error_code', '') == 14:
            log_string += " | " + get_string('err14', language)
    else:
        log_string += get_string('success', language)
    log_string += additional
    print(log_string)
    log_file.write(log_string + '\n')


delays = {'normal': (0, 1), 'captcha': (2, 3)}
attempts_limit = 5

parameters_for_deleting = dict.fromkeys(to_delete_str_arr, [])

if 'likes' in to_delete_str_arr:
    # print(get_string('deleting_likes', language))
    # log_file.write(get_string('deleting_likes', language) + '\n')
    likes_dir_list = os.listdir('Archive/likes')
    likes_dir_list = [i for i in likes_dir_list if os.path.isdir('Archive/likes/' + i)]
    for cur_dir_name in likes_dir_list:
        likes_files = os.listdir('Archive/likes/' + cur_dir_name)
        for cur_file_name in likes_files:
            cur_file = open('Archive/likes/' + cur_dir_name + '/' + cur_file_name, 'r')
            lines = cur_file.readlines()
            for line in lines:
                cur_dir_name_split = cur_dir_name.split('_')[0]
                if cur_dir_name_split in line:
                    link = line.split('"')[1]
                    content_type = cur_dir_name_split
                    owner_id, second_part = link.split(content_type)[1].split('_')
                    item_id, *reply_id = second_part.split('?reply=')

                    reply_id = reply_id[0] if len(reply_id) > 0 else ''

                    parameters_for_deleting['likes'].append({'link': link, 'method': 'likes.delete',
                                                             'params': {'type': content_type, 'owner_id': int(owner_id),
                                                                        'item_id': int(item_id)}})

if 'comments' in to_delete_str_arr:
    comments_file_list = os.listdir('Archive/comments')

    for cur_file_name in comments_file_list:
        cur_file = open('Archive/comments/' + cur_file_name, 'r')
        lines = cur_file.readlines()
        for line in lines:
            if '<a href=' in line:
                link = line.split('<a href="')[1].split('">')[0]
                owner_id, second_part = link.split('wall')[1].split('_')
                item_id, reply_id = second_part.split('?reply=')
                if 'thread' in reply_id:
                    reply_id = reply_id.split('&')[0]

                parameters_for_deleting['comments'].append({'link': link, 'method': 'wall.deleteComment',
                                                            'params': {'owner_id': int(owner_id),
                                                                       'comment_id': int(reply_id)}})

if 'wall' in to_delete_str_arr:
    # print(get_string('deleting_wall', language))
    # log_file.write(get_string('deleting_wall', language) + '\n')
    wall_files = os.listdir('Archive/wall')
    wall_files = [i for i in wall_files if not os.path.isdir('Archive/wall/' + i)]
    for cur_file_name in wall_files:
        cur_file = open('Archive/wall/' + cur_file_name, 'r')
        lines = cur_file.readlines()
        for line in lines:
            if 'href="https://vk.com/wall' in line:
                link = line.split('href="')[1].split('">')[0]

                owner_id, post_id = link.split('wall')[1].split('_')

                parameters_for_deleting['wall'].append({'link': link, 'method': 'wall.delete',
                                                        'params': {'owner_id': int(owner_id), 'post_id': int(post_id)}})

if 'photos_in_messages' in to_delete_str_arr:
    msg_dirs = os.listdir('Archive/messages')
    msg_dirs = [i for i in msg_dirs if os.path.isdir('Archive/messages/' + i)]

    msgs_id = []

    progress_counter = 0
    for cur_msg_dir in msg_dirs:
        # res = vk_api.execute_method('messages.getHistoryAttachments', {'peer_id':cur_msg_dir, 'media_type': 'photo', 'count': 200})
        # print(res)

        msg_files = os.listdir('Archive/messages/' + cur_msg_dir)
        for cur_file_name in msg_files:
            print('Archive/messages/' + cur_msg_dir + '/' + cur_file_name)
            cur_file = open('Archive/messages/' + cur_msg_dir + '/' + cur_file_name, 'r')
            lines = cur_file.readlines()

            document = HTMLDocument(''.join(lines))

            msgs_docs = document.get_elements_by_attributes({'class': 'message'})

            def filter_msg(msg_doc):
                doc = HTMLDocument(msg_doc)
                return doc.check_attributes({'class': 'attachment'})

            msgs_docs = list(filter(filter_msg, msgs_docs))

            msgs_id.extend([i['attrs']['data-id'][0] for i in msgs_docs])

        #     for line in lines:
        #         if 'data-id=' in line:
        #             msg_id = line.split('data-id="')[1].split('"')[0]
        #             msgs_id.append(msg_id)
        progress_counter = progress_counter + 1
        print(get_string('archive_messages_parsing', language).format(progress_counter / len(msg_dirs)))

    msgs = []

    for i in range(1, int(len(msgs_id) / 100) + 2):
        tmp = vk_api.execute_method('messages.getById', {'message_ids': ', '.join(msgs_id[(i - 1) * 100:i * 100])})[
            'response']['items']
        print(get_string('getting_list_of_msg', language).format(i / (int(len(msgs_id) / 100) + 1)))
        msgs.extend(tmp)


    # msgs = vk_api.execute_method('messages.getById', {'message_ids': ', '.join(msgs_id)})['response']['items']

    def filter_func(msg):
        for attachment in msg['attachments']:
            if attachment['type'] == 'photo' and attachment['photo']['owner_id'] == user_id:
                return True
        return False


    msgs = list(filter(filter_func, msgs))

    print(len(msgs))

    for msg in msgs:
        for attachment in msg['attachments']:
            if attachment['type'] == 'photo':
                photo = attachment['photo']
                parameters_for_deleting['photos_in_messages'].append({'link': 'no_link', 'method': 'photos.restore',
                                                                      'params': {'owner_id': photo['owner_id'],
                                                                                 'photo_id': photo['id']}})

indexes = dict.fromkeys(to_delete_str_arr, 0)

while True:
    done = True
    for key in parameters_for_deleting.keys():
        print("Deleting", key, sep=' ')
        log_file.write('Deleting ' + key + '\n')
        for i in range(indexes[key], len(parameters_for_deleting[key])):
            line = parameters_for_deleting[key][i]

            res = vk_api.execute_method(line['method'], line['params'])

            build_log_str(res=res, link=line['link'], log_file=log_file)

            time.sleep(random.randint(delays['normal'][0], delays['normal'][1]))

            fail_counter = 1

            while res.get('error', {'error_code': 0}).get('error_code', 0) == 14:
                fail_counter = fail_counter + 1
                res = vk_api.execute_method(line['method'], line['params'])

                build_log_str(res=res, link=line['link'], log_file=log_file,
                              additional=" | " + get_string('attempt_limit',
                                                            language) if fail_counter >= attempts_limit else '')
                if fail_counter >= attempts_limit:
                    break
                time.sleep(random.randint(delays['captcha'][0], delays['captcha'][1]))

            indexes[key] = indexes[key] + 1

            if fail_counter >= attempts_limit:
                indexes[key] = indexes[key] - 1
                break

    for key in parameters_for_deleting.keys():
        if indexes[key] < len(parameters_for_deleting[key]) - 1:
            done = False

    if done:
        break

print(get_string('done', language))
log_file.write(get_string('done', language) + '\n')
log_file.close()


