def get_args(num_of_args, allowed_args, start_msg="Enter value:", err_msg="Invalid value!", args_msgs=[], arg_type=int,
             mode="inline"):
    if mode == "auto":
        print(start_msg)
        first_input = input().strip()
        if len(first_input.split(" ")) > 1:
            return get_args_inline(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg, err_msg=err_msg,
                                   args_msgs=args_msgs,
                                   arg_type=arg_type, first_input=first_input)
        else:
            return get_args_line_by_line(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg, err_msg=err_msg,
                                         args_msgs=args_msgs,
                                         arg_type=arg_type, first_input=first_input)
    elif mode == "inline":
        return get_args_inline(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg, err_msg=err_msg,
                               args_msgs=args_msgs,
                               arg_type=arg_type)
    elif mode == "line_by_line":
        return get_args_line_by_line(num_of_args=num_of_args, allowed_args=allowed_args, start_msg=start_msg, err_msg=err_msg,
                                     args_msgs=args_msgs,
                                     arg_type=arg_type)


def get_args_inline(num_of_args, allowed_args, start_msg="Enter value:", err_msg="Invalid value!", args_msgs=[], arg_type=int,
                    first_input=""):

    is_first = True
    args = []
    if first_input:
        args = [arg_type(j) for j in first_input.split(" ")]
        is_first = False

    def check_arg(args_for_check, allowed_args):
        if len(args_for_check) < num_of_args or num_of_args==-1 and is_first:
            return False
        if isinstance(allowed_args, list):
            for i in args_for_check:
                if not (arg_type(i) in allowed_args):
                    return False
            return True
        else:
            for i in args_for_check:
                if not allowed_args(arg_type(i)):
                    return False
            return True

    while (not check_arg(args, allowed_args)):
        if not is_first:
            print(err_msg)
        print(start_msg)
        tmp = input().strip().split(" ")
        args = [arg_type(j) for j in tmp]
        is_first = False
    return args[:num_of_args] if num_of_args > 0 else args


def get_args_line_by_line(num_of_args, allowed_args, start_msg="Enter value:", err_msg="Invalid value!", args_msgs=[],
                          arg_type=int, first_input="not_setted"):
    def check_arg(args, allowed_args):
        if isinstance(allowed_args, list):
            if not (arg_type(args) in allowed_args):
                return False
            return True
        else:
            if not allowed_args(arg_type(args)):
                return False
            return True

    if not args_msgs:
        args_msgs = [""] * num_of_args

    args = [0] * num_of_args
    if not first_input:
        print(start_msg)
    for i in range(0, num_of_args):

        if i == 0 and first_input != "not_setted":
            tmp = first_input
        else:
            print(args_msgs[i])
            tmp = input()
        while (not check_arg(tmp, allowed_args)):
            print(err_msg)
            print(args_msgs[i])
            tmp = input()
        args[i] = arg_type(tmp)
    return args
