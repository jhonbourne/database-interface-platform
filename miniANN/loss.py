from .module import Module

class _Loss(Module):
    def __init__(self, reduction='mean'):
        super().__init__()
        assert reduction in ('mean','sum','none'), \
            "The 'reduction' parameter must be 'mean', 'sum', or 'none'."
        self.reduction = reduction

    def _apply_redution(self, loss_tensor):
        if self.reduction == 'mean':
            return loss_tensor.mean()
        elif self.reduction == 'sum':
            return loss_tensor.sum()
        else:
            return loss_tensor
        
class MSELoss(_Loss):
    def __init__(self, reduction='mean'):
        super().__init__(reduction)

    def forward(self, predictions, targets):
        err = predictions - targets
        loss = err.pow(2)
        return self._apply_redution(loss)
    
    