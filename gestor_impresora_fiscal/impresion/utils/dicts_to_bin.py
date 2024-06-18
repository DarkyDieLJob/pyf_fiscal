

def dict_to_bin(dic):
    dic = {bin(k)[2:]: v for k, v in dic.items()}
    #print(dic)
    return dic

def dict_to_int(dic):
    dic = {int(k): v for k, v in dic.items()}
    #print(dic)
    return dic