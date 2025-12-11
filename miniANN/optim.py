


class Optimizer:
    def __init__(self, params):
        self.param_groups = list(params)

    def step(self):
        raise NotImplementedError
    
    def zero_grad(self):
        for param in self.param_groups:
            if param.grad is not None:
                param.grad.fill(0.0)

class SGD(Optimizer):
    def __init__(self, params, lr=0.01):
        super().__init__(params)
        self.lr = lr

    def step(self):
        for param in self.param_groups:
            if param.grad is not None:
                param.data -= self.lr * param.grad