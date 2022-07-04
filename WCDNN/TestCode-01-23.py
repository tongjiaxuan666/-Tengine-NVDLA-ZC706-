# File    : Test.py
# Author  : Liu Rui
# Date    : 2021/10/7
# version : V0.0.0 
# Contact : Liur@cqu.edu.cn
# Description : This code is used to ... 

import os
import random
import torch
# torch.set_default_dtype(torch.float32)
import time
import math
import numpy as np
import pandas as pd  # 用于读取 excel 数据的包
from torch import nn, optim
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset
from torchsummary import summary

name = '01-23'
batch_size = 1000
lr = 1e-3
epochs = 200
device = torch.device('cuda:0')

# 在神经网络中，参数默认是随机初始化的。设置随机种子堆，保证每次训练时参数初始化都是固定的，训练结果也是不变的
def setup_seed(seed):
    torch.manual_seed(seed)  # 为 CPU 训练 设置随机数中种子
    torch.cuda.manual_seed_all(seed)  # 为 GPU 训练 设置随机数中种子
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
setup_seed(1)

savepath = '../Result/CWRU_bearing/WDCNN/'


class WDCNN(nn.Module):
    def __init__(self):
        super(WDCNN, self).__init__()
        self.w1 = nn.Parameter(torch.Tensor(16, 1, 64).type(torch.float32))
        self.w1.data.uniform_(-1. / math.sqrt(5), 1. / math.sqrt(5))
        self.b1 = nn.Parameter(torch.Tensor(16).type(torch.float32))
        self.b1.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w2 = nn.Parameter(torch.Tensor(32, 16, 3).type(torch.float32))
        self.w2.data.uniform_(-1. / math.sqrt(5), 1. / math.sqrt(5))
        self.b2 = nn.Parameter(torch.Tensor(32).type(torch.float32))
        self.b2.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w3 = nn.Parameter(torch.Tensor(64, 32, 3).type(torch.float32))
        self.w3.data.uniform_(-1. / math.sqrt(3), 1. / math.sqrt(3))
        self.b3 = nn.Parameter(torch.Tensor(64).type(torch.float32))
        self.b3.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w4 = nn.Parameter(torch.Tensor(64, 64, 3).type(torch.float32))
        self.w4.data.uniform_(-1. / math.sqrt(3), 1. / math.sqrt(3))
        self.b4 = nn.Parameter(torch.Tensor(64).type(torch.float32))
        self.b4.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w5 = nn.Parameter(torch.Tensor(64, 64, 3).type(torch.float32))
        self.w5.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))
        self.b5 = nn.Parameter(torch.Tensor(64).type(torch.float32))
        self.b5.data.uniform_(-1. / math.sqrt(512), 1. / math.sqrt(512))

        self.gamma = nn.Parameter(torch.Tensor(192).type(torch.float32))
        self.gamma.data.uniform_(-1. / math.sqrt(100), 1. / math.sqrt(100))
        self.beta = nn.Parameter(torch.Tensor(192).type(torch.float32))
        self.beta.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w7 = nn.Parameter(torch.Tensor(100, 192).type(torch.float32))
        self.w7.data.uniform_(-1. / math.sqrt(100), 1. / math.sqrt(100))
        self.b7 = nn.Parameter(torch.Tensor(100).type(torch.float32))
        self.b7.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

        self.w8 = nn.Parameter(torch.Tensor(10, 100).type(torch.float32))
        self.w8.data.uniform_(-1. / math.sqrt(100), 1. / math.sqrt(100))
        self.b8 = nn.Parameter(torch.Tensor(10).type(torch.float32))
        self.b8.data.uniform_(-1. / math.sqrt(1), 1. / math.sqrt(1))

    def forward(self, x):
        out = F.conv1d(x, self.w1, self.b1, stride=16, padding=24)
        out = nn.MaxPool1d(kernel_size=2, stride=2)(out)
        out = F.conv1d(out, self.w2, self.b2, stride=1, padding=1)
        out = nn.MaxPool1d(2, stride=2)(out)
        out = F.conv1d(out, self.w3, self.b3, stride=1, padding=1)
        out = nn.MaxPool1d(2, stride=2)(out)
        out = F.conv1d(out, self.w4, self.b4, stride=1, padding=1)
        out = nn.MaxPool1d(2, stride=2)(out)
        out = F.conv1d(out, self.w5, self.b5, stride=1, padding=0)
        out = nn.MaxPool1d(2, stride=2)(out)
        out = nn.Flatten()(out)
        # out = nn.BatchNorm1d(192, eps=1e-05, device=device)(out)
        out = (out - torch.mean(out)) / torch.sqrt(torch.var(out) + 1e-5) * self.gamma + self.beta
        out = F.linear(out, weight=self.w7, bias=self.b7)
        out = nn.LeakyReLU(0.1)(out)
        out = F.linear(out, weight=self.w8, bias=self.b8)
        out = nn.LeakyReLU(0.1)(out)
        return out


# 量化后的 WDCNN 模型
def quantifiedWDCNN(x, w1, b1, w2, b2, w3, b3, w4, b4, w5, b5, gamma, beta, w7, b7, w8, b8):
    y = F.conv1d(x, w1, b1, stride=16, padding=24)
    y = nn.MaxPool1d(2, stride=2)(y)
    y = F.conv1d(y, w2, b2, stride=1, padding=1)
    y = nn.MaxPool1d(2, stride=2)(y)
    y = F.conv1d(y, w3, b3, stride=1, padding=1)
    y = nn.MaxPool1d(2, stride=2)(y)
    y = F.conv1d(y, w4, b4, stride=1, padding=1)
    y = nn.MaxPool1d(2, stride=2)(y)
    y = F.conv1d(y, w5, b5, stride=1, padding=0)
    y = nn.MaxPool1d(2, stride=2)(y)
    y = nn.Flatten()(y)
    # y = nn.BatchNorm1d(8000).cuda(gpu)(y)
    y =(y-torch.mean(y))/torch.sqrt(torch.var(y)+1e-5)*gamma+beta
    y = F.linear(y, weight=w7, bias=b7)
    y = nn.LeakyReLU(0.1)(y)
    y = F.linear(y, weight=w8, bias=b8)
    y = nn.LeakyReLU(0.1)(y)
    return y


def data_set():
    # 读入csv中原始振动数据，默认导入后为 numpy 中的 ndarray 多维数组类型，维度： [batch, len]
    dataset0 = pd.read_csv('../Data/CWRU_Bearing/train-0hp-1797rpm.csv', header=None).values
    dataset1 = pd.read_csv('../Data/CWRU_Bearing/train-1hp-1772rpm.csv', header=None).values
    dataset2 = pd.read_csv('../Data/CWRU_Bearing/train-2hp-1750rpm.csv', header=None).values
    dataset3 = pd.read_csv('../Data/CWRU_Bearing/train-3hp-1730rpm.csv', header=None).values

    # 把 numpy 转为 tensor, 同时更改数据类型和变换维度为 [batch, 1, len]
    dataset0 = torch.tensor(dataset0).unsqueeze(dim=1).to(device, dtype=torch.float32)
    dataset1 = torch.tensor(dataset1).unsqueeze(dim=1).to(device, dtype=torch.float32)
    dataset2 = torch.tensor(dataset2).unsqueeze(dim=1).to(device, dtype=torch.float32)
    dataset3 = torch.tensor(dataset3).unsqueeze(dim=1).to(device, dtype=torch.float32)

    # 拼接训练集，划分测试集
    trainSet = torch.cat((dataset0, dataset1), dim=0)
    train_x, train_y = trainSet[:, :, 0:-1], trainSet[:, :, -1]
    trainSet = TensorDataset(train_x, train_y)  # 将 data 与 label 打包封装
    # DataLoader将 dataset 按照 batch_size 进行迭代分装, 返回得一个 iterator，可用
    trainSet = DataLoader(trainSet, batch_size=batch_size, shuffle=True)

    testSet = torch.cat((dataset2, dataset3), dim=0)
    test_x, test_y = testSet[:, :, 0:-1], testSet[:, :, -1]
    testSet = TensorDataset(test_x, test_y)
    testSet = DataLoader(testSet, batch_size=8000, shuffle=True)

    return trainSet, testSet, test_x, test_y


def quantified(a, intbit=4, opibit=5):  # 12位定点量化： 1位符号位+4个整数位+7小数位
    b = np.clip(a, -math.pow(2, intbit), math.pow(2, intbit)-1)  # 数据限幅
    b = np.round(b * math.pow(2, opibit) + 0.5) / math.pow(2, opibit)
    b = torch.from_numpy(b)  # 得到最接近原始a的定点数
    return b


def main():

    # 载入数据集和模型
    trainSet, testSet, test_x, test_y = data_set()
    model = WDCNN().to(device)
    summary(model.cuda(), input_size=(1, 2048), batch_size=1000)

    # 定义优化器和 loss 评判准则
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss().to(device)

    # Float32标准数据类型训练网络
    trainLoss = torch.zeros(epochs)
    testAcc1, testTime1 = torch.zeros(epochs), torch.zeros(epochs)
    testAcc2, testTime2 = torch.zeros(epochs), torch.zeros(epochs)
    model.train()
    for epoch in range(epochs):

        LOSS = 0
        for batchIdx, (x, label) in enumerate(trainSet):
            # CrossEntropyLoss 要求 label 是 one-hot 和 Long 类型
            label = label.squeeze().long()
            logits = model(x)
            loss = criterion(logits, label)
            trainLoss[epoch] = loss.item()
            # 网络参数更新
            optimizer.zero_grad()  # gradient clearing
            loss.backward()  # gradient calculation and back-propagation
            optimizer.step()  # parameters update
            LOSS += loss.item()
        trainLoss[epoch] = LOSS / (batchIdx + 1)  # 多个batch的平均trainloss
        print(epoch, 'epoch, 训练Loss:', LOSS/(batchIdx+1))

        # 训练后对 WDCNN 网络参数进行量化，并创建 weight 和 bias 的全局变量
        for name, param in model.named_parameters():
            # globals()[name] = param.data.type(torch.float16).type(torch.float32).cpu()
            globals()[name] = quantified(param.data.cpu().numpy())

        # Float32标准数据类型评估结果
        model.eval()
        with torch.no_grad():
            correctNum = 0
            totalNum = 0
            for x, target in testSet:
                # x = x.half()
                # target = target.half()
                target = target.squeeze()
                start = time.time()
                logits = model(x)
                end = time.time()
                pred = logits.argmax(dim=-1)
                correctNum += torch.eq(pred, target).sum().item()
                totalNum += target.size(0)
        acc = correctNum / totalNum
        testAcc1[epoch] = acc
        testTime1[epoch] = end - start
        print(epoch, 'epoch, 标准模型测试准确率: {:.4%}'.format(acc), ' >> [{}/{}]'.format(correctNum, totalNum))


        # 测试数据量化，test_x 和 test_y
        test_x = quantified(test_x.cpu().numpy())
        test_y = quantified(test_y.cpu().numpy())
        start = time.time()
        logits = quantifiedWDCNN(test_x, w1, b1, w2, b2, w3, b3, w4, b4, w5, b5, gamma, beta, w7, b7, w8, b8)
        end = time.time()
        test_pred = logits.argmax(dim=1)
        correctNum = torch.eq(test_pred, test_y.view(test_y.shape[0])).float().sum().item()
        acc = correctNum/test_x.size(0)
        testAcc2[epoch] = acc
        testTime2[epoch] = end - start
        print(epoch, 'epoch, 量化模型测试准确率: {:.4%}'.format(acc), ' >> [{}/{}]'.format(correctNum, totalNum))

    return test_pred, trainLoss, testAcc1, testTime1, testAcc2, testTime2



if __name__ == '__main__':
    pred, trainLoss, testAcc1, testTime1, testAcc2, testTime2 = main()
    print('float32位测试最大准确率：{:.4f}'.format(torch.max(testAcc1).item()))
    print('float32位测试平均准确率：{:.4f}'.format(torch.mean(testAcc1[epochs-50:epochs]).item()))
    print('float32位测试平均用时(s)：{:.4f}'.format(torch.mean(testTime1[epochs-50:epochs]).item()))

    print('float32位测试最大准确率：{:.4f}'.format(torch.max(testAcc2).item()))
    print('float32位测试平均准确率：{:.4f}'.format(torch.mean(testAcc2[epochs-50:epochs]).item()))
    print('float32位测试平均用时(s)：{:.4f}'.format(torch.mean(testTime2[epochs-50:epochs]).item()))

    print('识别准确率比值(量化模型/Float32模型)：{:.4f}'.format(torch.mean(testAcc2[epochs-50:epochs]).item() / torch.mean(testAcc1[epochs - 50:epochs]).item()))

    if os.path.exists(savepath) == False:
        os.mkdir(savepath)
    np.savetxt(savepath + '/' + name + '-量化预测pred.csv', pred.int().cpu(), fmt="%.4d")
    np.savetxt(savepath + '/' + name + '-训练Loss.csv', trainLoss.cpu(), fmt="%.4f")
    np.savetxt(savepath + '/' + name + '-标准模型识别精度.csv', testAcc1.cpu(), fmt="%.4f")
    np.savetxt(savepath + '/' + name + '-量化模型识别精度.csv', testAcc1.cpu(), fmt="%.4f")



