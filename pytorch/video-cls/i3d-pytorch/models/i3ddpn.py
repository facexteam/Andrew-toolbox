""" PyTorch implementation of DualPathNetworks
Ported to PyTorch by [Ross Wightman](https://github.com/rwightman/pytorch-dpn-pretrained)

Based on original MXNet implementation https://github.com/cypw/DPNs with
many ideas from another PyTorch implementation https://github.com/oyam/pytorch-DPNs.

This implementation is compatible with the pretrained weights
from cypw's MXNet implementation.
"""
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.model_zoo as model_zoo
from collections import OrderedDict

__all__ = ['I3DDPN', 'i3d_dpn68', 'i3d_dpn68b', 'i3d_dpn92', 'i3d_dpn98', 'i3d_dpn131', 'i3d_dpn107']

pretrained_settings = {
    'i3d_dpn68': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn68-66bebafa7.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    },
    'i3d_dpn68b': {
        'imagenet+5k': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn68b_extra-84854c156.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    },
    'i3d_dpn92': {
        # 'imagenet': {
        #     'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn68-66bebafa7.pth',
        #     'input_space': 'RGB',
        #     'input_size': [3, 224, 224],
        #     'input_range': [0, 1],
        #     'mean': [124 / 255, 117 / 255, 104 / 255],
        #     'std': [1 / (.0167 * 255)] * 3,
        #     'num_classes': 1000
        # },
        'imagenet+5k': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn92_extra-b040e4a9b.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    },
    'i3d_dpn98': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn98-5b90dec4d.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    },
    'i3d_dpn131': {
        'imagenet': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn131-71dfe43e0.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    },
    'i3d_dpn107': {
        'imagenet+5k': {
            'url': 'http://data.lip6.fr/cadene/pretrainedmodels/dpn107_extra-1ac7121e2.pth',
            'input_space': 'RGB',
            'input_size': [3, 224, 224],
            'input_range': [0, 1],
            'mean': [124 / 255, 117 / 255, 104 / 255],
            'std': [1 / (.0167 * 255)] * 3,
            'num_classes': 1000
        }
    }
}

def i3d_dpn68(num_classes=1000, pretrained='imagenet'):
    model = I3DDPN(
        small=True, num_init_features=10, k_r=128, groups=32,
        k_sec=(3, 4, 12, 3), inc_sec=(16, 32, 32, 64),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn68'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        model.load_state_dict(model_zoo.load_url(settings['url']))
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def i3d_dpn68b(num_classes=1000, pretrained='imagenet+5k'):
    model = I3DDPN(
        small=True, num_init_features=10, k_r=128, groups=32,
        b=True, k_sec=(3, 4, 12, 3), inc_sec=(16, 32, 32, 64),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn68b'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        pretrained_model = model_zoo.load_url(settings['url'])
        model = inflat_weights(pretrained_model, model)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def i3d_dpn92(num_classes=1000, pretrained='imagenet+5k'):
    model = I3DDPN(
        num_init_features=64, k_r=96, groups=32,
        k_sec=(3, 4, 20, 3), inc_sec=(16, 32, 24, 128),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn92'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        pretrained_model = model_zoo.load_url(settings['url'])
        model = inflat_weights(pretrained_model, model)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def i3d_dpn98(num_classes=1000, pretrained='imagenet'):
    model = I3DDPN(
        num_init_features=96, k_r=160, groups=40,
        k_sec=(3, 6, 20, 3), inc_sec=(16, 32, 32, 128),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn98'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        pretrained_model = model_zoo.load_url(settings['url'])
        model = inflat_weights(pretrained_model, model)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def i3d_dpn131(num_classes=1000, pretrained='imagenet'):
    model = I3DDPN(
        num_init_features=128, k_r=160, groups=40,
        k_sec=(4, 8, 28, 3), inc_sec=(16, 32, 32, 128),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn131'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        pretrained_model = model_zoo.load_url(settings['url'])
        model = inflat_weights(pretrained_model, model)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def i3d_dpn107(num_classes=1000, pretrained='imagenet+5k'):
    model = I3DDPN(
        num_init_features=128, k_r=200, groups=50,
        k_sec=(4, 8, 20, 3), inc_sec=(20, 64, 64, 128),
        num_classes=num_classes, test_time_pool=True)
    if pretrained:
        settings = pretrained_settings['i3d_dpn107'][pretrained]
        assert num_classes == settings['num_classes'], \
            "num_classes should be {}, but is {}".format(settings['num_classes'], num_classes)

        pretrained_model = model_zoo.load_url(settings['url'])
        model = inflat_weights(pretrained_model, model)
        model.input_space = settings['input_space']
        model.input_size = settings['input_size']
        model.input_range = settings['input_range']
        model.mean = settings['mean']
        model.std = settings['std']
    return model

def inflat_weights(model_dict_2d, model_3d):
    model_dict_3d = model_3d.state_dict()
    for key,weight_2d in model_dict_2d.items():
        if key in model_dict_3d:
            if '.conv.' in key:
                time_kernel_size = model_dict_3d[key].shape[2]
                if 'weight' in key:
                    weight_3d = weight_2d.unsqueeze(2).repeat(1,1,time_kernel_size,1,1)
                    weight_3d = weight_3d / time_kernel_size
                    model_dict_3d[key] = weight_3d
                elif 'bias' in key:
                    model_dict_3d[key] = weight_2d
            elif '.bn.' in key:
                    model_dict_3d[key] = weight_2d
            elif 'classifier' in key:
                model_dict_3d[key] = weight_3d

                if 'weight' in key:
                    time_kernel_size = model_dict_3d[key].shape[1] / weight_2d.shape[1]
                    weight_3d = weight_2d.repeat(1, time_kernel_size)
                    weight_3d = weight_3d / time_kernel_size
                    model_dict_3d[key] = weight_3d
                elif 'bias' in key:
                    model_dict_3d[key] = weight_2d

    model_3d.load_state_dict(model_dict_3d)
    return model_3d


class CatBnAct(nn.Module):
    def __init__(self, in_chs, activation_fn=nn.ReLU(inplace=True)):
        super(CatBnAct, self).__init__()
        self.bn = nn.BatchNorm3d(in_chs, eps=0.001)
        self.act = activation_fn

    def forward(self, x):
        x = torch.cat(x, dim=1) if isinstance(x, tuple) else x
        return self.act(self.bn(x))


class BnActConv3d(nn.Module):
    def __init__(self, in_chs, out_chs, kernel_size, stride,
                 padding=0, groups=1, activation_fn=nn.ReLU(inplace=True)):
        super(BnActConv3d, self).__init__()
        self.bn = nn.BatchNorm3d(in_chs, eps=0.001)
        self.act = activation_fn
        self.conv = nn.Conv3d(in_chs, out_chs, kernel_size, stride, padding, groups=groups, bias=False)

    def forward(self, x):
        return self.conv(self.act(self.bn(x)))


class InputBlock(nn.Module):
    def __init__(self, num_init_features, kernel_size=(5,7,7),
                 padding=(2,3,3), stride=(2,2,2), activation_fn=nn.ReLU(inplace=True)):
        super(InputBlock, self).__init__()
        self.conv = nn.Conv3d(
            3, num_init_features, kernel_size=kernel_size, stride=stride, padding=padding, bias=False)
        self.bn = nn.BatchNorm3d(num_init_features, eps=0.001)
        self.act = activation_fn
        self.pool = nn.MaxPool3d(kernel_size=(3,3,3), stride=(2,2,2), padding=(1,1,1))

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.act(x)
        x = self.pool(x)
        return x


class DualPathBlock3D(nn.Module):
    def __init__(
            self, in_chs, num_1x1_a, num_3x3_b, num_1x1_c, inc, groups, block_type='normal', b=False, time_kernel=1):
        super(DualPathBlock3D, self).__init__()
        self.num_1x1_c = num_1x1_c
        self.inc = inc
        self.b = b
        if block_type is 'proj':
            self.key_stride = 1
            self.has_proj = True
        elif block_type is 'down':
            self.key_stride = 2
            self.has_proj = True
        else:
            assert block_type is 'normal'
            self.key_stride = 1
            self.has_proj = False

        if self.has_proj:
            # Using different member names here to allow easier parameter key matching for conversion
            if self.key_stride == 2:
                self.c1x1_w_s2 = BnActConv3d(
                    in_chs=in_chs, out_chs=num_1x1_c + 2 * inc, kernel_size=(1,1,1), stride=(1,2,2))
            else:
                self.c1x1_w_s1 = BnActConv3d(
                    in_chs=in_chs, out_chs=num_1x1_c + 2 * inc, kernel_size=(1,1,1), stride=(1,1,1))
        self.c1x1_a = BnActConv3d(in_chs=in_chs, out_chs=num_1x1_a, kernel_size=(time_kernel,1,1), stride=(1,1,1),
                                  padding=((time_kernel-1)//2,0,0))
        self.c3x3_b = BnActConv3d(
            in_chs=num_1x1_a, out_chs=num_3x3_b, kernel_size=(1,3,3),
            stride=(1,self.key_stride,self.key_stride), padding=(0,1,1), groups=groups)
        if b:
            self.c1x1_c = CatBnAct(in_chs=num_3x3_b)
            self.c1x1_c1 = nn.Conv3d(num_3x3_b, num_1x1_c, kernel_size=(1,1,1), bias=False)
            self.c1x1_c2 = nn.Conv3d(num_3x3_b, inc, kernel_size=(1,1,1), bias=False)
        else:
            self.c1x1_c = BnActConv3d(in_chs=num_3x3_b, out_chs=num_1x1_c + inc, kernel_size=(1,1,1), stride=(1,1,1))

    def forward(self, x):
        x_in = torch.cat(x, dim=1) if isinstance(x, tuple) else x
        if self.has_proj:
            if self.key_stride == 2:
                x_s = self.c1x1_w_s2(x_in)
            else:
                x_s = self.c1x1_w_s1(x_in)
            x_s1 = x_s[:, :self.num_1x1_c, :, :]
            x_s2 = x_s[:, self.num_1x1_c:, :, :]
        else:
            x_s1 = x[0]
            x_s2 = x[1]
        x_in = self.c1x1_a(x_in)
        x_in = self.c3x3_b(x_in)
        if self.b:
            x_in = self.c1x1_c(x_in)
            out1 = self.c1x1_c1(x_in)
            out2 = self.c1x1_c2(x_in)
        else:
            x_in = self.c1x1_c(x_in)
            out1 = x_in[:, :self.num_1x1_c, :, :]
            out2 = x_in[:, self.num_1x1_c:, :, :]
        resid = x_s1 + out1
        dense = torch.cat([x_s2, out2], dim=1)
        return resid, dense

class TemporalPool(nn.Module):
    def __init__(self, kernel_size=(3, 1, 1), stride=(2, 1, 1), padding=(1, 0, 0)):
        super(TemporalPool, self).__init__()
        self.temporalpool = nn.MaxPool3d(kernel_size=kernel_size, stride=stride, padding=padding)

    def forward(self,x):
        x_in = torch.cat(x, dim=1) if isinstance(x, tuple) else x
        x_out = self.temporalpool(x_in)
        return x_out

class I3DDPN(nn.Module):
    def __init__(self, small=False, num_init_features=64, k_r=96, groups=32,
                 b=False, k_sec=(3, 4, 20, 3), inc_sec=(16, 32, 24, 128),
                 num_classes=1000, test_time_pool=False, frame_num=32):
        super(I3DDPN, self).__init__()
        self.test_time_pool = test_time_pool
        self.frame_num = frame_num
        self.b = b
        bw_factor = 1 if small else 4

        blocks = OrderedDict()

        # conv1
        if small:
            blocks['conv1_1'] = InputBlock(num_init_features, kernel_size=(2,3,3), padding=(0,1,1), stride=(2,2,2))
        else:
            blocks['conv1_1'] = InputBlock(num_init_features, kernel_size=(5,7,7), padding=(2,3,3), stride=(2,2,2))

        # conv2
        bw = 64 * bw_factor
        inc = inc_sec[0]
        r = (k_r * bw) // (64 * bw_factor)
        time_kernel=3
        blocks['conv2_1'] = DualPathBlock3D(num_init_features, r, r, bw, inc, groups, 'proj', b, time_kernel=time_kernel)
        in_chs = bw + 3 * inc
        for i in range(2, k_sec[0] + 1):
            if i % 2 == 0:
                time_kernel = 1
            else:
                time_kernel = 3
            blocks['conv2_' + str(i)] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'normal', b, time_kernel=time_kernel)
            in_chs += inc
        blocks['temporalpool'] = TemporalPool(kernel_size=(3, 1, 1), stride=(2, 1, 1), padding=(1, 0, 0))
        # conv3
        bw = 128 * bw_factor
        inc = inc_sec[1]
        r = (k_r * bw) // (64 * bw_factor)
        time_kernel = 3
        blocks['conv3_1'] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'down', b, time_kernel=time_kernel)
        in_chs = bw + 3 * inc
        for i in range(2, k_sec[1] + 1):
            if i % 2 == 0:
                time_kernel = 1
            else:
                time_kernel = 3
            blocks['conv3_' + str(i)] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'normal', b, time_kernel=time_kernel)
            in_chs += inc

        # conv4
        bw = 256 * bw_factor
        inc = inc_sec[2]
        r = (k_r * bw) // (64 * bw_factor)
        time_kernel = 3
        blocks['conv4_1'] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'down', b, time_kernel=time_kernel)
        in_chs = bw + 3 * inc
        for i in range(2, k_sec[2] + 1):
            if i % 2 == 0:
                time_kernel = 1
            else:
                time_kernel = 3
            blocks['conv4_' + str(i)] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'normal', b, time_kernel=time_kernel)
            in_chs += inc

        # conv5
        bw = 512 * bw_factor
        inc = inc_sec[3]
        r = (k_r * bw) // (64 * bw_factor)
        time_kernel = 3
        blocks['conv5_1'] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'down', b, time_kernel=time_kernel)
        in_chs = bw + 3 * inc
        for i in range(2, k_sec[3] + 1):
            if i % 2 == 0:
                time_kernel = 1
            else:
                time_kernel = 3
            blocks['conv5_' + str(i)] = DualPathBlock3D(in_chs, r, r, bw, inc, groups, 'normal', b, time_kernel=time_kernel)
            in_chs += inc
        blocks['conv5_bn_ac'] = CatBnAct(in_chs)

        self.features = nn.Sequential(blocks)

        # Using 1x1 conv for the FC layer to allow the extra pooling scheme
        self.classifier = nn.Conv3d(in_chs, num_classes, kernel_size=(1,1,1), bias=True)

    def logits(self, features):
        if not self.training and self.test_time_pool:
            x = F.avg_pool3d(features, kernel_size=(self.frame_num//8,7,7), stride=1)
            out = self.classifier(x)
            # The extra test time pool should be pooling an img_size//32 - 6 size patch
            out = adaptive_avgmax_pool2d(out, pool_type='avgmax')
        else:
            x = adaptive_avgmax_pool2d(features, pool_type='avg')
            out = self.classifier(x)
        return out.view(out.size(0), -1)

    def forward(self, input):
        x = self.features(input)
        x = self.logits(x)
        return x

""" PyTorch selectable adaptive pooling
Adaptive pooling with the ability to select the type of pooling from:
    * 'avg' - Average pooling
    * 'max' - Max pooling
    * 'avgmax' - Sum of average and max pooling re-scaled by 0.5
    * 'avgmaxc' - Concatenation of average and max pooling along feature dim, doubles feature dim

Both a functional and a nn.Module version of the pooling is provided.

Author: Ross Wightman (rwightman)
"""
def adaptive_avgmax_pool2d(x, pool_type='avg', padding=0, count_include_pad=False):
    """Selectable global pooling function with dynamic input kernel size
    """
    if pool_type == 'avgmaxc':
        x = torch.cat([
            F.avg_pool3d(
                x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding, count_include_pad=count_include_pad),
            F.max_pool3d(x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding)
        ], dim=1)
    elif pool_type == 'avgmax':
        x_avg = F.avg_pool3d(
                x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding, count_include_pad=count_include_pad)
        x_max = F.max_pool3d(x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding)
        x = 0.5 * (x_avg + x_max)
    elif pool_type == 'max':
        x = F.max_pool3d(x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding)
    else:
        if pool_type != 'avg':
            print('Invalid pool type %s specified. Defaulting to average pooling.' % pool_type)
        x = F.avg_pool3d(
            x, kernel_size=(x.size(2), x.size(3), x.size(4)), padding=padding, count_include_pad=count_include_pad)
    return x


if __name__ == '__main__':
    import torchvision
    import numpy as np
    import torch
    from torch.autograd import Variable
    from dpn import dpn107

    dpn107_2d = dpn107()
    dpn107_i3d = i3d_dpn107()

    data = np.ones((1, 3, 224, 224), dtype=np.float32)
    tensor = torch.from_numpy(data)
    inputs = Variable(tensor)
    out1 = dpn107_2d(inputs)
    print(out1)

    data2 = np.ones((1, 3, 32, 224, 224), dtype=np.float32)
    tensor2 = torch.from_numpy(data2)
    inputs2 = Variable(tensor2)
    out2 = dpn107_i3d(inputs2)
    print(out2)