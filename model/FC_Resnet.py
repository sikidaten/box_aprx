import torch
import torch.nn as nn
import torch.nn.functional as F
class BasicBlock(nn.Module):
    def __init__(self, feature,batchnorm=False):
        super(BasicBlock, self).__init__()
        self.fc1 = nn.Linear(feature, feature)
        self.fc2 = nn.Linear(feature, feature)
        self.bn1=nn.BatchNorm1d(feature)
        self.bn2=nn.BatchNorm1d(feature)
        self.batchnorm=batchnorm

    def forward(self, x):
        _x = x
        x = self.fc1(x)
        if self.batchnorm:
            x=self.bn1(x)
        x = F.relu(x)
        x = self.fc2(x)
        if self.batchnorm:
            x=self.bn2(x)
        x = F.relu(x)
        x = _x + x
        x = F.relu(x)
        return x


class BottleNeck(nn.Module):
    def __init__(self, feature, fn_act=nn.ReLU(),batchnorm=False):
        super(BottleNeck, self).__init__()
        self.fcs = nn.ModuleList([nn.Linear(feature, feature) for _ in range(3)])
        self.bns = nn.ModuleList([nn.BatchNorm1d(feature) for _ in range(3)])
        self.fn_act = fn_act
        self.batchnorm=batchnorm
    def forward(self, x):
        _x = x
        x = self.fcs[0](x)
        if self.batchnorm:
            x=self.bns[0](x)
        x=self.fn_act(x)
        x = self.fcs[1](x)
        if self.batchnorm:
            x=self.bns[1](x)
        x=self.fn_act(x)
        x = self.fcs[2](x)
        if self.batchnorm:
            x=self.bns[2](x)
        return self.fn_act(x + _x)


class FC_ResNet(nn.Module):
    def __init__(self, block, layers=(1, 2, 3, 4), features=(128, 128, 256, 512), fn_activate=nn.ReLU(),flow_loss=False,batchnorm=False):
        super(FC_ResNet, self).__init__()
        self.infc = nn.Linear(116, features[0])
        self.fcs = nn.ModuleList(
            [nn.Sequential(
                *[block(features[idx],batchnorm) for _ in range(l)]
            ) for idx, l in enumerate(layers)]
        )
        self.changer=nn.ModuleList([nn.Linear(in_feature,out_feature) for in_feature,out_feature in zip(features[:-1],features[1:])])
        self.outfc = nn.Linear(features[-1], 20)
        self.activate = fn_activate
        self.flow_loss=flow_loss
    def forward(self, x):
        x = self.activate(self.infc(x))
        for idx,fc in enumerate(self.fcs):
            x = fc(x)
            if idx<3:
                x=self.changer[idx](x)
        x=self.outfc(x)
        return [x]


def fc_resnet18():
    return FC_ResNet(layers=[2, 2, 2, 2], block=BasicBlock,batchnorm=True)


def fc_resnet34():
    return FC_ResNet(layers=[3, 4, 6, 3], block=BasicBlock)


def fc_resnet50():
    return FC_ResNet(layers=[3, 4, 6, 3], block=BottleNeck)


def fc_resnet101():
    return FC_ResNet(layers=[3, 4, 23, 3], block=BottleNeck)


def fc_resnet152():
    return FC_ResNet(layers=[3, 8, 36, 3], block=BottleNeck)

if __name__=='__main__':
    model=fc_resnet18()
    optimizer=torch.optim.Adam(model.parameters())
    output=model(torch.randn(3,116))
    loss=output.mean()
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()