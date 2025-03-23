from collections.abc import Callable
from typing import Literal


def get_args(num_of_args: int,
             allowed_args: list | Callable,
             start_msg: str = "Enter value:",
             err_msg: str = "Invalid value!",
             args_msgs: list = None,
             arg_type: type = int,
             print_func: Callable = print,
             mode: Literal['auto', 'line_by_line', 'inline'] = "inline"):
    if args_msgs is None:
        args_msgs = []
    if mode == "auto":
        print_func(start_msg)
        first_input = input().strip()
        if len(first_input.split()) > 1:
            return get_args_inline(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg,
                                   err_msg=err_msg,
                                   args_msgs=args_msgs,
                                   arg_type=arg_type,
                                   first_input=first_input,
                                   print_func=print_func)
        else:
            return get_args_line_by_line(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg,
                                         err_msg=err_msg,
                                         args_msgs=args_msgs,
                                         arg_type=arg_type,
                                         first_input=first_input,
                                         print_func=print_func)
    elif mode == "inline":
        return get_args_inline(num_of_args=num_of_args,
                               allowed_args=allowed_args,
                               start_msg=start_msg,
                               err_msg=err_msg,
                               args_msgs=args_msgs,
                               arg_type=arg_type,
                               print_func=print_func)
    elif mode == "line_by_line":
        return get_args_line_by_line(num_of_args=num_of_args,
                                     allowed_args=allowed_args,
                                     start_msg=start_msg,
                                     err_msg=err_msg,
                                     args_msgs=args_msgs,
                                     arg_type=arg_type,
                                     print_func=print_func)


def get_args_inline(num_of_args: int,
                    allowed_args: list | Callable,
                    start_msg: str = "Enter value:",
                    err_msg: str = "Invalid value!",
                    args_msgs: list = None,
                    arg_type: type = int,
                    print_func: Callable = print,
                    first_input: str = ""):
    is_first = True
    args = []
    if first_input:
        args = [arg_type(j) for j in first_input.split()]
        is_first = False

    def check_arg(values):
        if len(values) < num_of_args or num_of_args == -1 and is_first:
            return False
        if isinstance(allowed_args, list):
            for i in values:
                if not (arg_type(i) in allowed_args):
                    return False
        else:
            for i in values:
                if not allowed_args(arg_type(i)):
                    return False
        return True

    while not check_arg(args):
        if not is_first:
            print_func(err_msg)
        print_func(start_msg)
        tmp = input().strip().split()
        args = [arg_type(j) for j in tmp]
        is_first = False
    return args[:num_of_args]


def get_args_line_by_line(num_of_args: int,
                          allowed_args: list | Callable,
                          start_msg: str = "Enter value:",
                          err_msg: str = "Invalid value!",
                          args_msgs=None,
                          arg_type: type = int,
                          print_func: Callable=print,
                          first_input=None):
    def check_arg(value):
        if isinstance(allowed_args, list):
            if not (arg_type(value) in allowed_args):
                return False
            return True
        else:
            if not allowed_args(arg_type(value)):
                return False
            return True

    if not args_msgs:
        args_msgs = [""] * num_of_args

    args = [0] * num_of_args

    if not first_input:
        print_func(start_msg)

    for i in range(0, num_of_args):
        if i == 0 and first_input is not None:
            tmp = first_input
        else:
            print_func(args_msgs[i])
            tmp = input()
        while not check_arg(tmp):
            print_func(err_msg)
            print_func(args_msgs[i])
            tmp = input()
        args[i] = arg_type(tmp)
    return args
