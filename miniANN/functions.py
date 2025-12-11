"""Define arithmetic operations and their gradients"""
import numpy as np

class ContextManager:
    """Context manager to save values for backward computation"""
    def __init__(self):
        self.saved_tensors = []

    def save_for_backward(self, *tensors):
        # save the whole objects
        self.saved_tensors.extend(tensors)

    def get_saved_tensors(self):
        return self.saved_tensors
    
"""Both forward and backward function returns numpy array.
    Returned values in backward function should correspond to
    those inputs of forward function."""

def mat_transpose(ctx, tensor):
    if tensor.data.ndim < 2:
        out_data_view = tensor.data
    else:
        out_data_view = tensor.data.T
    return out_data_view
def mat_transpose_backward(ctx, grad_output):
    return grad_output.T
    
def add(ctx, tensor1, tensor2):
    # ctx.save_for_backward(tensor1, tensor2) # TODO for handling broadcasting
    result_data = tensor1.data + tensor2.data
    return result_data

def add_backward(ctx, grad_output):
    # tensor1, tensor2 = ctx.get_saved_tensors() # TODO for handling broadcasting
    grad_tensor1 = grad_output
    grad_tensor2 = grad_output
    return grad_tensor1, grad_tensor2

def sub(ctx, tensor1, tensor2):
    # ctx.save_for_backward(tensor1, tensor2) # TODO for handling broadcasting
    result_data = tensor1.data - tensor2.data
    return result_data

def sub_backward(ctx, grad_output):
    # tensor1, tensor2 = ctx.get_saved_tensors() # TODO for handling broadcasting
    grad_tensor1 = grad_output
    grad_tensor2 = -grad_output
    return grad_tensor1, grad_tensor2

def mul(ctx, tensor1, tensor2):
    ctx.save_for_backward(tensor1, tensor2)
    result_data = tensor1.data * tensor2.data
    return result_data

def mul_backward(ctx, grad_output):
    tensor1, tensor2 = ctx.get_saved_tensors()
    grad_tensor1 = grad_output * tensor2.data
    grad_tensor2 = grad_output * tensor1.data
    return grad_tensor1, grad_tensor2

def matmul(ctx, tensor1, tensor2):
    ctx.save_for_backward(tensor1, tensor2)
    result_data = np.matmul(tensor1.data, tensor2.data)
    return result_data

def matmul_backward(ctx, grad_output):
    tensor1, tensor2 = ctx.get_saved_tensors()
    try:
        grad_tensor1 = np.matmul(grad_output, tensor2.data.T)
    except ValueError:
        grad_tensor1 = np.outer(grad_output, tensor2.data)
    try:
        grad_tensor2 = np.matmul(tensor1.data.T, grad_output)
    except ValueError:
        grad_tensor2 = np.outer(tensor1.data, grad_output)
    return grad_tensor1, grad_tensor2

def sum_op(ctx, tensor, axis=None, keepdims=False):
    ctx.save_for_backward(tensor, axis, keepdims)
    result_data = np.sum(tensor.data, axis=axis, keepdims=keepdims)
    return result_data

def sum_backward(ctx, grad_output):
    tensor, axis, keepdims = ctx.get_saved_tensors()
    if axis is None:
        grad_tensor = np.ones_like(tensor.data) * (grad_output)
    else:
        grad_tensor = grad_output
        if not keepdims:
            shape = list(grad_tensor.shape)
            if isinstance(axis, int):
                axis = (axis,)
            for ax in sorted(axis): # Correctly restore dimensions by order
                shape.insert(ax, 1)
            grad_tensor = grad_tensor.reshape(shape)
        grad_tensor = np.broadcast_to(grad_tensor, tensor.data.shape)
    return grad_tensor

def mean_op(ctx, tensor, axis=None, keepdims=False):
    ctx.save_for_backward(tensor, axis, keepdims)
    result_data = np.mean(tensor.data, axis=axis, keepdims=keepdims)
    return result_data

def mean_backward(ctx, grad_output):
    tensor, axis, keepdims = ctx.get_saved_tensors()
    if axis is None:
        smp_num = tensor.data.size
    else:
        orig_shape = tensor.data.shape
        smp_num = np.ones([orig_shape[a] for a in axis]).size
    
    grad_tensor = sum_backward(ctx, grad_output)
    return grad_tensor / smp_num

def pow_op(ctx, tensor, power):
    assert isinstance(power, (int, float)), "Exponent must be a scalar."
    ctx.save_for_backward(tensor, power)
    result_data = np.power(tensor.data, power)
    return result_data

def pow_backward(ctx, grad_output):
    tensor, power = ctx.get_saved_tensors()
    grad_tensor = grad_output * power * np.power(tensor.data, power - 1)
    return grad_tensor

def log(ctx, tensor):
    """Clip zero for numerical stability"""
    eps = np.finfo(tensor.data.dtype).eps
    safe_data = np.clip(tensor.data, eps, None)
    
    ctx.save_for_backward(safe_data)
    result_data = np.log(safe_data)
    return result_data

def log_backward(ctx, grad_output):
    safe_data, = ctx.get_saved_tensors()
    grad_tensor = (1.0 / safe_data) * grad_output
    return grad_tensor

def exp(ctx, tensor):
    result_data = np.exp(tensor.data)
    ctx.save_for_backward(result_data)
    return result_data

def exp_backward(ctx, grad_output):
    exp_output, = ctx.get_saved_tensors()
    grad_tensor = grad_output * exp_output
    return grad_tensor

def sigmoid(ctx, tensor):
    result_data = 1 / (1 + np.exp(-tensor.data))
    ctx.save_for_backward(result_data)
    return result_data

def sigmoid_backward(ctx, grad_output):
    sigmoid_output, = ctx.get_saved_tensors()
    grad_tensor = grad_output * sigmoid_output * (1 - sigmoid_output)
    return grad_tensor

def relu(ctx, tensor):
    result_data = np.maximum(0, tensor.data)
    ctx.save_for_backward(tensor)
    return result_data

def relu_backward(ctx, grad_output):
    tensor, = ctx.get_saved_tensors()
    grad_tensor = grad_output * (tensor.data > 0) # Set gradient to 0 where input <= 0
    return grad_tensor

def softmax(ctx, tensor, axis=-1):
    """Consider numerical stability"""
    x = tensor.data
    x_max = np.max(x, axis=axis, keepdims=True)
    shifted_x = x - x_max
    # Calculate softmax
    # s_i = exp(z_i) / sum_j(exp(z_j))
    exp_x = np.exp(shifted_x)
    sum_exp = np.sum(exp_x, axis=axis, keepdims=True)
    result_data = exp_x / sum_exp # Using broadcasting

    ctx.save_for_backward(result_data, axis)
    return result_data

def softmax_backward(ctx, grad_output):
    softmax_output, axis = ctx.get_saved_tensors()

    # Efficient calculation formula:
    # dL/dz = s * (dL/ds - sum(dL/ds *s))
    grad_dotX_output = grad_output * softmax_output
    sum_dotX = np.sum(grad_dotX_output, axis=axis, keepdims=True)
    grad_tensor = softmax_output * (grad_output - sum_dotX)
    return grad_tensor

# Register the forward/backward pairs of operations
FUNCTION_MAP = {
    '.T': (mat_transpose, mat_transpose_backward),
    'add': (add, add_backward),
    'sub': (sub, sub_backward),
    'mul': (mul, mul_backward),
    'matmul': (matmul, matmul_backward),
    'sum': (sum_op, sum_backward),
    'mean': (mean_op, mean_backward),
    'pow': (pow_op, pow_backward),
    'log': (log, log_backward),
    'exp': (exp, exp_backward),
    'sigmoid': (sigmoid, sigmoid_backward),
    'relu': (relu, relu_backward),
    'softmax': (softmax, softmax_backward)
}