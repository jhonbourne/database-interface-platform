from functools import partial
import numpy as np

from .tensor_core import Tensor
from .module import Module

GAIN_TABLE = {
    'tanh': 5/3,
    'relu': 2**0.5
}

def kaiming_init(nonlinearity='other', fan_mode=None, distribution='normal'):
    def get_scale_param(gain, dist_gain, fan_mode):
        return gain * dist_gain / (fan_mode**0.5)
    
    gain = GAIN_TABLE.get(nonlinearity.lower(), 1)

    if distribution == 'normal':
        dist_gain = 3**0.5
        rand_gen = partial(np.random.normal,
                           loc=0,
                           scale=get_scale_param(gain,dist_gain,fan_mode))
    elif distribution == 'uniform':
        rand_gen = np.random.uniform
        dist_gain = 1
        scale_param = get_scale_param(gain,dist_gain,fan_mode)
        rand_gen = partial(np.random.uniform,
                           low=-scale_param, high=scale_param)
    else:
        raise ValueError("Invalid input for 'distribution'!")

    return rand_gen

class Linear(Module):
    def __init__(self, in_dim, out_dim, mode='fan_in', **kwargs):
        super().__init__()
        
        # Use kaiming initialization by default
        if 'in' in mode:
            fan_mode = in_dim
        elif 'out' in mode:
            fan_mode = out_dim
        else:
            raise ValueError("Invalid input for 'mode'!")
        rand_gen = kaiming_init(fan_mode=fan_mode, **kwargs)

        self.weight = Tensor(
            rand_gen(size=(out_dim, in_dim)),
            requires_grad=True
        )
        self.bias = Tensor(
            rand_gen(size=out_dim),
            requires_grad=True
        )

    def forward(self, x):
        if not isinstance(x, Tensor):
            raise TypeError("Input of forward computation must be Tensor.")
        _o = (self.weight @ x)
        return _o + self.bias