import os
import re
from typing import Generator


def _parse_likes_in_file(extracted_archive_path: str, file_name: str) -> Generator:
    comments_file_list = os.listdir(f'{extracted_archive_path}/comments')

    link_regex = r'https://vk.com/[a-z]+[-0-9]+_[0-9]+\?\w+\=[-0-9]+\&*\w*\=*[-0-9]*'

    with open(f'{extracted_archive_path}/comments/{file_name}', 'r') as f:
        text = f.read()

    for match in re.findall(link_regex, text):
        owner_id = re.search(r'[-0-9]+', match).group()
        reply_id = re.search(r'reply=[-0-9]+', match).group()
        thread_id = re.search(r'thread=[-0-9]+', match)
        comment_id = reply_id
        if thread_id is not None:
            thread_id = thread_id.group()
            comment_id = thread_id
        yield {'link': match, 'method': 'wall.deleteComment',
                                                        'params': {'owner_id': int(owner_id),
                                                                   'comment_id': int(comment_id)}}


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