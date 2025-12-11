from functools import reduce
import numpy as np

from .functions import FUNCTION_MAP, ContextManager

class Tensor:
    def __init__(self, data, _children=(), _op='',
                 requires_grad=False):
        self.data = np.array(data) if not isinstance(data, np.ndarray) else data
        self.grad = np.zeros_like(self.data) if requires_grad else None
        self._backward = lambda: None  # function to compute gradient
        self._prev = set([c for c in _children if isinstance(c,Tensor)])    # set of parent Tensors
        self._op = _op                  # operation that produced this Tensor

        self.requires_grad = requires_grad
    def _apply_op(self, op_name, *tensors):
        # Dealing the operation function
        fw_func, bw_func = FUNCTION_MAP.get(op_name, (None,None))
        if fw_func is None or bw_func is None:
            raise NotImplementedError(f"Operation '{op_name}' not implemented.")
        
        ctx = ContextManager()

        
        tensors4op = [t if isinstance(t, Tensor) else t for t in tensors]
        output_data = fw_func(ctx, *tensors4op)
        # When an operation create a new tensor, register the operation and
        # tensors used in this operation in the new tensor, so gradient can trace back
        output_tensor = Tensor(output_data, _children=tensors, _op=op_name,
                               requires_grad=any([t.requires_grad for t in tensors if isinstance(t, Tensor)])
                               )

        def _backward():
            grad_output = output_tensor.grad
            # Calculate the gradient of this operation
            grads_input = bw_func(ctx, grad_output)

            grads_input = grads_input if isinstance(grads_input, (tuple,list)) \
                                    else (grads_input,)
            for tensor, grad_in in zip(tensors, grads_input):
                if isinstance(tensor, Tensor):
                    if tensor.requires_grad:
                        tensor.grad += grad_in
                    # TODO for broadcasting conditions

        output_tensor._backward = _backward

        return output_tensor
    
    def backward(self):
        nodes = []
        visited = set()
        def build_topo(v): # Use recursion
            if v not in visited:
                visited.add(v) # Node traverse
                for child in v._prev:
                    build_topo(child)
                nodes.append(v) # Start from the deepest nodes
        build_topo(self)

        # Common practices? Loss is assumed to be a scalar.
        assert self.data.squeeze().ndim == 0, "Only scalar is allowed for calling backward"
        self.grad = np.array(1.0)
        for node in reversed(nodes): # Back propagation start from shallow node
            node._backward()


    # ------- Operator for tensors -------
    @property
    def T(self):
        return self._apply_op('.T', self)
    
    # def __neg__(self): TODO: if use tensor1 = -tensor2

    def __add__(self, other):
        return self._apply_op('add', self, other)
    
    def __sub__(self, other):
        return self._apply_op('sub', self, other)
    
    def __mul__(self, other):
        return self._apply_op('mul', self, other)
    
    def matmul(self, other):
        return self._apply_op('matmul', self, other)

    def __matmul__(self, other):
        return self.matmul(other)
    
    def sum(self):
        return self._apply_op('sum', self)
    
    def mean(self):
        return self._apply_op('mean', self)
    
    def pow(self, exponent):
        return self._apply_op('pow', self, exponent)
    
    def log(self):
        return self._apply_op('log', self)
    
    def exp(self):
        return self._apply_op('exp', self)
    
    def sigmoid(self):
        return self._apply_op('sigmoid', self)
    
    def relu(self):
        return self._apply_op('relu', self)
    
    def softmax(self):
        return self._apply_op('softmax', self)