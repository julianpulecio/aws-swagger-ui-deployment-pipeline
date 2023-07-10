def find_value_by_key(iterable:iter, key:str) -> any:
    if isinstance(iterable, dict):
        result = find_value_by_key_in_dict(iterable, key)
        if result != None:
            return result
         
    if isinstance(iterable, list):
        result = find_value_by_key_in_list(iterable, key)
        if result != None:
            return result

def find_value_by_key_in_list(list_:list, key:str):
    for element in list_:
        result = find_value_by_key(element, key)
        if result != None:
            return result

def find_value_by_key_in_dict(dict_:dict, key:str):
    if key in dict_:
        return dict_[key]
    for _, value in dict_.items():
        result = find_value_by_key(value, key)
        if result != None:
            return result