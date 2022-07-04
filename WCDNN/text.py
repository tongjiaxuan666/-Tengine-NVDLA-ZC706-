import torch
import math
import numpy as np
from torch import nn
from torch.nn import init


def t1(a, intbit=4, opibit=7):  # 12位定点量化
    b = a.detach().numpy()  # 由于a是训练参数，requires_grad为True，因此不能直接用numpy函数操作，需转换
    b = np.clip(b, -math.pow(2, intbit), math.pow(2, intbit)-1)  # 0.9995117187是1 - (1/2)^11
    b = np.round(b * math.pow(2, opibit) + 0.5) / math.pow(2, opibit)  # 2048是2^11
    b = torch.from_numpy(b)  # 得到最接近原始a的定点数
    return b

a = torch.tensor([14.031]).type(torch.float32)
b = t1(a, intbit=4, opibit=7).numpy()
c = torch.tensor(np.round(a.cpu().numpy()*math.pow(2, 7))/math.pow(2, 7))
print(a)
print(b)
print(c)
