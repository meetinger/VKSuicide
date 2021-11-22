def getArgs(numOfArgs, allowedArgs, startMsg="Enter value:", errMsg="Invalid value!", argsMsgs=[], argType=int,
            mode="inline"):
    if mode == "auto":
        print(startMsg)
        first_input = input().strip()
        if len(first_input.split(" ")) > 1:
            return getArgsInline(numOfArgs=numOfArgs, allowedArgs=allowedArgs, startMsg=startMsg, errMsg=errMsg,
                                 argsMsgs=argsMsgs,
                                 argType=argType, firstInput=first_input)
        else:
            return getArgsLineByLine(numOfArgs=numOfArgs, allowedArgs=allowedArgs, startMsg=startMsg, errMsg=errMsg,
                                     argsMsgs=argsMsgs,
                                     argType=argType, firstInput=first_input)
    elif mode == "inline":
        return getArgsInline(numOfArgs=numOfArgs, allowedArgs=allowedArgs, startMsg=startMsg, errMsg=errMsg,
                             argsMsgs=argsMsgs,
                             argType=argType)
    elif mode == "line_by_line":
        return getArgsLineByLine(numOfArgs=numOfArgs, allowedArgs=allowedArgs, startMsg=startMsg, errMsg=errMsg,
                                 argsMsgs=argsMsgs,
                                 argType=argType)


def getArgsInline(numOfArgs, allowedArgs, startMsg="Enter value:", errMsg="Invalid value!", argsMsgs=[], argType=int,
                  firstInput=""):

    isFirst = True
    args = []
    if firstInput:
        args = [argType(j) for j in firstInput.split(" ")]
        isFirst = False

    def checkArg(args, allowedArgs):
        if len(args) < numOfArgs or numOfArgs==-1 and isFirst:
            return False
        if isinstance(allowedArgs, list):
            for i in args:
                if not (argType(i) in allowedArgs):
                    return False
            return True
        else:
            for i in args:
                if not allowedArgs(argType(i)):
                    return False
            return True

    while (not checkArg(args, allowedArgs)):
        if not isFirst:
            print(errMsg)
        print(startMsg)
        tmp = input().strip().split(" ")
        args = [argType(j) for j in tmp]
        isFirst = False
    return args[:numOfArgs] if numOfArgs > 0 else args


def getArgsLineByLine(numOfArgs, allowedArgs, startMsg="Enter value:", errMsg="Invalid value!", argsMsgs=[],
                      argType=int, firstInput="not_setted"):
    def checkArg(args, allowedArgs):
        if isinstance(allowedArgs, list):
            if not (argType(args) in allowedArgs):
                return False
            return True
        else:
            if not allowedArgs(argType(args)):
                return False
            return True

    if not argsMsgs:
        argsMsgs = [""] * numOfArgs

    args = [0] * numOfArgs
    if not firstInput:
        print(startMsg)
    for i in range(0, numOfArgs):

        if i == 0 and firstInput != "not_setted":
            tmp = firstInput
        else:
            print(argsMsgs[i])
            tmp = input()
        while (not checkArg(tmp, allowedArgs)):
            print(errMsg)
            print(argsMsgs[i])
            tmp = input()
        args[i] = argType(tmp)
    return args
