# File    : WDCNN.py
# Author  : Liu Rui
# Date    : 2021/10/7
# version : V0.0.0 
# Contact : Liur@cqu.edu.cn
# Description : This code is used to ... 
'''
import torch
import onnx
from torch import nn, optim
from torchsummary import  summary
from onnxsim import simplify
#device = torch.device('cuda')


class WDCNN(nn.Module):
    def __init__(self):
        super(WDCNN, self).__init__()
        self.feature = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=64, stride=16, padding=24),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(kernel_size=2, stride=2)
            nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Conv1d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Conv1d(64, 64, kernel_size=3, stride=1, padding=0),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Flatten()
        )
        self.fc = nn.Sequential(
            nn.Linear(192, 100).type(torch.float32), nn.LeakyReLU(0.1),
            nn.Linear(100, 10).type(torch.float32), nn.LeakyReLU(0.1)
        )

    def forward(self, x):
        out = self.feature(x)
        out = self.fc(out)
        return out


def main():
    input_names = ["input_0"]
    output_names = ["output_0"]
    temp = torch.randn([32, 1, 2048])#to(device)
    model = WDCNN()#to(device)
    #out = model(temp)
    #out=model()
    model.eval()
    dummy_input=torch.randn(1,1,2048)
    torch.onnx.export(model, dummy_input, 'wdcnn.onnx',opset_version=10)#dynamic_axes={'input_0': [0], 'output_0': [0]})
    #print(out.shape)
    print('finished exporting onnx')


if __name__ == '__main__':
    main()
'''
'''
WDCNN model with pytorch

Reference:
Wei Zhang, Gaoliang Peng, Chuanhao Li, Yuanhang Chen and Zhujun Zhang
A New Deep Learning Model for Fault Diagnosis with Good Anti-Noise and Domain Adaptation Ability on Raw Vibration Signals
Sensors, MDPI
doi:10.3390/s17020425
'''
import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=(1, 3), stride=(1, 1), padding=(0, 1)):
        super(BasicBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=padding, bias=True)
        self.bn = nn.BatchNorm2d(out_channels)
        self.pool = nn.MaxPool2d((1, 2),stride=(1, 2))
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.conv(x)
        out = self.bn(out)
        out = self.pool(out)
        out = self.relu(out)
        return out

class Net(nn.Module):
    def __init__(self, in_channels, n_class, use_feature=False):
        super(Net, self).__init__()
        self.name = 'WDCNN'
        self.use_feature = use_feature
        #self.b0 = nn.BatchNorm2d(in_channels)
        self.b1 = BasicBlock(in_channels, 16, kernel_size=(1, 64), stride=(1, 16), padding=(0, 24)) #根据公式计算得出padding[0]=0
        self.b2 = BasicBlock(16, 32)
        self.b3 = BasicBlock(32, 64)
        self.b4 = BasicBlock(64, 64)
        self.b5 = BasicBlock(64, 64, padding=(0, 0))
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(192, 100)
        self.fc2 = nn.Linear(100, n_class)

    def forward(self, x):
        #x = self.b0(x)
        x = self.b1(x)
        x = self.b2(x)
        x = self.b3(x)
        x = self.b4(x)
        x = self.b5(x)
        x = self.flatten(x)
        x = self.fc1(x)
        y = self.fc2(x)
        #features = (f0,f1,f2,f3,f4,f5)
        #activations = self.fc(features[-1].view(-1, self.n_features))
        #if self.use_feature:
        #   out = (activations, features)
        #else:
        #    out = activations
        return y
'''
net = Net(1, 4)
x = torch.randn(10,1,2048)
y = net(Variable(x))
print(y.size)
'''
def main():
    model = Net(1,4)#to(device)
    #out = model(temp)
    #out=model()
    model.eval()
    dummy_input=torch.randn(1,1,1,2048)
    torch.onnx.export(model, dummy_input, 'wdcnn.onnx',opset_version=10)#dynamic_axes={'input_0': [0], 'output_0': [0]})
    #print(out.shape)
    print('finished exporting onnx')


if __name__ == '__main__':
    main()