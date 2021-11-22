def extract_from_dictionary(dictionary, keys_or_indexes):
    value = dictionary
    for key_or_index in keys_or_indexes:
        value = value[key_or_index]
    return value
