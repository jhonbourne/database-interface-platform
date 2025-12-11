import numpy as np
import pickle

from .tensor_core import Tensor

"""Seems complicated to implement an usable Parameter class"""
# class Parameter(Tensor):
#     def __new__(cls, data=None, requires_grad=True):
#         if data is None:
#             data = Tensor()
#         if not isinstance(data, Tensor):
        
    
class Module:
    def __init__(self):
        self._parameters = {}
        self._modules = {}

    def __setattr__(self, name, value):
        if isinstance(value, Tensor) and value.requires_grad:
            self._parameters[name] = value

        elif isinstance(value, Module): # Recursion
            self._modules[name] = value

        super().__setattr__(name, value) # default method should be called

    def parameters(self):
        for param in self._parameters.values():
            yield param
        for module in self._modules.values():
            yield from module.parameters() # Recursion

    def zero_grad(self):
        for p in self.parameters():
            if p.grad is not None:
                p.grad.fill(0.0)

    def state_dict(self):
        """Return a dictionary with all the parameters included"""
        state = {}
        def _add_params(module, prefix=''):
            for name, param in module._parameters.items():
                key = f"{prefix}.{name}" if prefix else name
                # save data (ndarray) of Tensor
                state[key] = param.data 
            for name, submodule in module._modules.items():
                submodule_prefix = f"{prefix}.{name}" if prefix else name
                _add_params(submodule, submodule_prefix)
        
        _add_params(self)
        return state

    def load_state_dict(self, state_dict):
        """Load parameter from dictionary"""
        def _load_params(module, prefix=''):
            for name, param in module._parameters.items():
                key = f"{prefix}.{name}" if prefix else name
                if key in state_dict:
                    
                    if param.data.shape != state_dict[key].shape:
                        raise ValueError(f"Shape mismatch for parameter {key}")
                    # Load data
                    param.data[:] = state_dict[key]
                else:
                    print(f"Warning: Parameter {key} not found in state_dict")
            
            for name, submodule in module._modules.items():
                submodule_prefix = f"{prefix}.{name}" if prefix else name
                _load_params(submodule, submodule_prefix)
        
        _load_params(self)

    def save(self, filepath):
        """Save model parameters"""
        state = self.state_dict()
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
        print(f"Model state dict saved to {filepath}")

    @staticmethod
    def load(filepath, model_class, *args, **kwargs):
        """Load parameters to a new instance"""
        # class definition is needed
        model = model_class(*args, **kwargs)
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        model.load_state_dict(state)
        print(f"Model state dict loaded from {filepath}")
        return model
