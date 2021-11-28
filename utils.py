def extract_from_dictionary(dictionary, keys_or_indexes):
    value = dictionary
    for key_or_index in keys_or_indexes:
        value = value[key_or_index]
    return value


def find_all(string: str, substring: str):
    l1 = []
    length = len(string)
    index = 0
    while index < length:
        i = string.find(substring, index)
        if i == -1:
            return l1
        l1.append(i)
        index = i + 1
    return l1


def progress_bar(length, cur, total, additional_str=''):
    progress = cur / total
    done = round(length*progress)
    eta = length-done
    bar = f'\r[{"#"*done}{"-"*eta}] { "{:.2%}".format(progress)}{" | "+additional_str if additional_str else ""}'
    print(bar, end='')
