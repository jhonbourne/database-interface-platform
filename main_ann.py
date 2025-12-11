import os
import numpy as np
import cv2

import miniANN as ann


dataset_path = r'C:\Users\JohnBourne\Documents\MS25\MNIST_CSV'
train_file = 'mnist_train.csv'
test_file = 'mnist_test.csv'

n_class = 10


def get_dataset(data_list, label_list):
    return list(zip(data_list, label_list))

# =========== Model Definition ===============

class Net(ann.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = ann.layer.Linear(28*28, 256)
        self.af1 = lambda x: x.sigmoid()
        self.fc2 = ann.layer.Linear(256, 10)
        self.af2 = lambda x: x.sigmoid()

    def forward(self, x):
        """x: Tensor
        return Tensor"""
        o1 = self.af1(self.fc1.forward(x))
        o2 = self.af2(self.fc2.forward(o1))
        return o2

    def in_norm(self, x):
        """x: numpy.ndarray
        return Tensor"""
        if not x.shape == (28,28):
            if x.size == 28*28 and x.ndim == 1:
                img = x
            else:
                img = np.array(cv2.resize(x, (28,28)))
        else:
            img = x

        flatten_img = img.flatten()
        return ann.Tensor(flatten_img)
    
    @staticmethod
    def get_pred(output):
        """output: Tensor
        return int"""
        return int(np.argmax(output.data))

def get_onehot(target, n_class):
    vec = np.zeros(n_class) + 0.01; vec[target] = 0.99
    return ann.Tensor(vec)
model = Net()

# =========== Training Definition =============
def eval(model, dataset):
    pred_labs = []; true_labs = []
    for data, label in dataset:
        output = model.forward(model.in_norm(data))
        pred = model.get_pred(output)
        pred_labs.append(pred)
        true_labs.append(label)
    pred_labs = np.array(pred_labs)
    true_labs = np.array(true_labs)
    acc = np.mean(pred_labs == true_labs)
    return acc

def train(model, train_dataset, val_dataset,
           criterion, optimizer, n_epoch, n_in_batch):
    order_inds = np.arange(len(train_dataset))
    for iEp in range(n_epoch):
        np.random.shuffle(order_inds)
        # init metric in batch
        run_n_smp = 0
        cnt = 0
        running_loss = 0.0
        optimizer.zero_grad()
        for idx in order_inds:
            data, label = train_dataset[idx]
            
            output = model.forward(model.in_norm(data))
            loss = criterion.forward(output, get_onehot(label, n_class))
            loss.backward()
            running_loss += loss.data

            cnt += 1
            run_n_smp +=1
            if cnt == n_in_batch:
                optimizer.step()
                optimizer.zero_grad()
                if run_n_smp % (int(int(len(order_inds)/n_in_batch)/10) * n_in_batch)== 0:
                    print(f'Epoch [{iEp+1}], Sample#{run_n_smp} , Training Loss: {running_loss:.4f}')
                    running_loss = 0.0
                    val_acc = eval(model, val_dataset)
                    print(f'Validation Accuracy: {val_acc*100:.3f} %')
                cnt = 0
        # print(f'Validation Accuracy after Epoch [{iEp+1}]: {val_acc*100:.3f} %')

if __name__ == '__main__':

    # ============ Dataset loading ==============
    # read training data
    with open(os.path.join(dataset_path,train_file),'r') as f:
        data_list = f.readlines()
    n_in_train = len(data_list)

    # split train/validation set
    valid_ind = np.random.choice(n_in_train, 5000, replace=False)

    train_data = []; train_labels = []
    valid_data = []; valid_labels = []
    for i,s in enumerate(data_list):
        vals = s.split(',')
        # rescale input vector
        input = (np.asarray(vals[1:],dtype=np.float64) / 255.0) * 0.99 + 0.1
        # target label index
        target = int(vals[0])
        # target = np.zeros(n_class) + 0.01; target[int(vals[0])] = 0.99

        if i in valid_ind:
            valid_data.append(input)
            valid_labels.append(target)
        else:
            train_data.append(input)
            train_labels.append(target)

    # read test data
    with open(os.path.join(dataset_path,test_file),'r') as f:
        data_list = f.readlines()

    test_data = []; test_labels = []
    for s in data_list:
        vals = s.split(',')
        # rescale input vector
        input = (np.asarray(vals[1:],dtype=np.float64) / 255.0) * 0.99 + 0.1
        # target label index
        target = int(vals[0])

        test_data.append(input)
        test_labels.append(target)

    # ============== Model training ===============
    criterion = ann.loss.MSELoss()
    optimizer = ann.optim.SGD(model.parameters(),lr=0.01)
    train(model, get_dataset(train_data,train_labels),
        get_dataset(valid_data, valid_labels),
        criterion, optimizer, 50, 64)
    test_acc = eval(model, get_dataset(test_data, test_labels))
    if test_acc >= 0.93:
        model.save(f'model_testAcc_{test_acc:.6f}.pkl')