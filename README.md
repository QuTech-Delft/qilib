[![Coverage Status](https://coveralls.io/repos/github/QuTech-Delft/qilib/badge.svg?branch=dev)](https://coveralls.io/github/QuTech-Delft/qilib?branch=dev)

# QILib

Quantum Library for the Quantum Inspire platform

## Installation

The Quantum Inspire Library can be installed from PyPI via pip:

```
$ pip install qilib
```

### Installing from source
Clone the qilib repository from https://github.com/QuTech-Delft/qilib and install using pip:
```
$ git clone git@github.com:QuTech-Delft/qilib.git
$ cd qilib
$ python3 -m venv env
$ . ./env/bin/activate
(env) $ pip install .
```

For development install in editable mode:
```
(env) $ pip install -e .[dev]
```

### Install Mongo database
To use the MongoDataSetIOReader and MongoDataSetIOWriter a mongodb needs to be installed.
For Windows, Linux or OS X follow the instructions [here](https://docs.mongodb.com/v3.2/administration/install-community/)
on how to install the database.

After installing the database it has to be configured as [replica set](https://docs.mongodb.com/manual/replication/) by
typing:
```
mongod --replSet "rs0"
```
and from within the mongo shell initiate with:
```
rs.initiate()
```

## Testing

Run all unittests and collect the code coverage:
```
(env) $ coverage run --source="./src/qilib" -m unittest discover -s src/tests -t src
(env) $ coverage report -m
```

## Data set
The three main building blocks of the qilib data set are a DataArray, DataSet and a DataSetIO that provides a
storage backend for the DataSet.  

### DataArray
A DataArray is a wrapper around a numpy array and can be used as one. A data array can also have another, or multiple,
data arrays as setpoints. For example, in a 2D-scan, there will be a 1D DataArray for the x-axis variable specifying a discrete set of setpoints
for that variable, a 2D DataArray for the y-axis variable using the x-axis DataArray as its values and a 2D DataArray
for the measured value.

The DataArray constructor accepts either:
+ pre-defined data (numpy arrays)
+ array shapes (tuple)

The DataArray makes sure that the dimensions of the set arrays are correct with regards to the data array and vice
versa. That means, e.g., trying to set a 1D array of 10 elements as the data array with a 1D setpoint array of 8
elements will raise an error.

An example of a 2D measurement array, **z**, that is defined by the main setpoint array **x** and secondary setpoint
array **y**:

```
import numpy as np
from qilib.data_set import DataArray

x_size = 10
y_size = 5
x_points = np.array(range(x_size))
y_points = np.tile(np.array(range(y_size)), [x_size, 1])
x = DataArray(name="x", label="x-axis", unit="mV", is_setpoint=True, preset_data=x_points)
y = DataArray(name="y", label="y-axis", unit="mV", is_setpoint=True, preset_data=y_points)
z = DataArray(name="z", label="z-axis", unit="ma", set_arrays=(x,y), shape=(x_size, y_size))

```

### DataSet
A DataSet object encompasses DataArrays. A DataSet can have multiple measurement arrays sharing the same setpoints.
It is an error to have multiple measurement arrays with different setpoints in one DataSet.

A DataSet can be incrementally updated with the `add_data()` method, which takes an index specification, a reference to
the array that is to be updated and the update data: `index, {array_name: update_data}}`. In case of multi dimensional
arrays whole rows, or rows of rows, can be updated together. For example:
```
# this sets a single element at the 3rd setpoint along the x-axis, 4th along the y-axis
dataset.add_data((2,3), {'z': 0.23})

# given that dataset is a 10 x 3 2D dataset:
# this sets the entire y-axis data at the 5th setpoint along the x-axis
# ie. the data specifies a value for each of the setpoints along the y-axis
dataset.add_data(4, {'z': [0.23, 2.6, 0.42]})
```

DataSet specifications:
+ The constructor may accept DataArrays for setpoints and data arrays. Multiple measurement arrays may be specified as
a sequence.
+ The DataSet will raise errors on mismatches in array dimensions.
+ The DataSet will only accept an array if its name does not equal that of any array already in the DataSet.
+ Arrays can be read by the public property .data_arrays (a dict, key is the DataArray name, value the DataArray).
In addition, DataArrays are accessible as properties on the DataSet object (for example, an array with name 'x' added
to a DataSet data_set can be access as data_set.x).
+ Updates made to the DataSet will be sent to the underlying DataSetIOWriter if available.
+ A DataSet can have one, or more, DataSetIOWriters.
+ A DataSet can be instantiated with one DataSetIOReader but not both a DataSetIOWriter and a DataSetIOReader.

### DataSetIOWriter
A DataSet can be instantiated with a DataSetIOWriter that provides a storage backend. All changes made on the DataSet
are pushed to the storage. There are two DataSetIOWriter implementation available, MemoryDataSetIOWriter and
MongoDataSetIOWriter.

#### MemoryDataSetIOWriter
Provides an in-memory storage backend that can be used for live plotting of a measurement. All data is kept in memory
and not stored on disc or in database. MemoryDataSetIOWriter should not be instantiated directly but created, along with
a MemoryDataSetIOReader, using the MemoryDataSetIOFactory. The Reader and Writer share a storage queue used to pass
updates from one DataSet to another.
```
io_reader, io_writer = MemoryDataSetIOFactory.get_reader_writer_pair()
data_set_consumer = DataSet(storage_reader=io_reader)
data_set_producer = DataSet(storage_writer=io_writer)
```

#### MongoDataSetIOWriter
Provides a connection to a mongo database that needs to be pre-installed. All updates to a DataSet are stored in the
mongodb database as events that are collapsed, to represent the complete DataSet, when the `finalize()` method is called
on the DataSet. Data can not be written to the database on a finalized DataSet.
```
data_set_name = 'experiment_42'
writer = MongoDataSetIOWriter(name=data_set_name)
data_set = DataSet(storage_writer=writer, name=data_set_name)
```

### DataSetIOReader
Classes that implement the DataSetIOReader interface allow a DataSet to subscribe to data, and data changes, in an
underlying storage. To sync from storage the `sync_from_storage(timeout)` method on a DataSet has to be called. There
are two implementations of the DataSetIOReader, the MemoryDataSetIOReader and MongoDataSetIOReader.

#### MemoryDataSetIOReader
Provides a way to subscribe to data that is put on a storage queue by a paired MemoryDataSetIOWriter created by the
MemoryDataSetIOFactory.

#### MongoDataSetIOReader
The MongoDataSetIOReader creates a connection to a mongodb and subscribes to changes in the underlying document. To
update a DataSet that has been instantiated with a MongoDataSetIOReader a call on the DataSet's `sync_from_storage(timeout)`
method has to be made. To load a DataSet from the underlying mongodb a static method `load(name, document_id)` can be
called with either the DataSet name or _id or both.

In the example below, a DataSet is instantiated with MongoDataSetIOReader, synced from storage and the data plotted:
```
consumer_dataset = MongoDataSetIOReader.load(name='experiment_42')
consumer_dataset.sync_from_storage(-1)
plot(consumer_dataset)

```

## Examples
#### Plot and measure with MemoryDataSetIO
In this example a MemoryDataSetIOWriter and MemoryDataSetIOReader pair is created using the MemoryDataSetIOFactory.
Fake measuremet is run on separate thread, feeding fake measurement data to in-memory storage that the consumer data set
syncs from with the `sync_from_storage(timeout)` method.
```python
import random
import threading
import time

import matplotlib.pyplot as plt

from qilib.data_set import DataSet, DataArray
from qilib.data_set.memory_data_set_io_factory import MemoryDataSetIOFactory

x_dim = 100
y_dim = 100
stop_measuring = False

io_reader, io_writer = MemoryDataSetIOFactory.get_reader_writer_pair()
data_set_consumer = DataSet(storage_reader=io_reader)
some_array = DataArray('some_array', 'label', shape=(x_dim, y_dim))
data_set_producer = DataSet(storage_writer=io_writer, data_arrays=some_array)

plt.ion()

def plot_measured_data():
    fig, ax = plt.subplots()
    for i in range(20):
        data_set_consumer.sync_from_storage(-1)
        ax.imshow(data_set_consumer.some_array, cmap='hot', interpolation='nearest')
        fig.canvas.draw()
    return True


def measure_data():
    while not stop_measuring:
        for i in range(x_dim):
            line = [i + j * random.random() for j in range(y_dim)]
            data_set_producer.add_data(i, {'some_array': line})
            time.sleep(0.02)


measure_thread = threading.Thread(target=measure_data)
measure_thread.start()
stop_measuring = plot_measured_data()
measure_thread.join()
```
#### Plot and measure with MongoDataSetIO
In this example one script creates a new DataSet with MongoDataSetIOWriter that stores a copy of the data set in a
underlying mongodb which needs to be pre-installed as described above. By instantiating the DataSet with a
MongoDataSetWriter all updates and additions to the DataSet are reflected in the database. To fetch the data set from
the database the static method `load(name, document_id)` provided in MongoDataSetIOReader is used. The method returns a
new DataSet object that subscribes to all changes in the underlying data set and can be updated with the
`sync_from_storage` method.

In one console run script __A__ and __B__ in another one. Make sure start script __A__ before __B__ as the former
creates the data set in the database that the latter attempts to load.

##### A
```python
import random
from time import sleep

import numpy as np

from qilib.data_set import DataSet, DataArray, MongoDataSetIOWriter

x_dim = 100
y_dim = 100

measurements = DataArray(name="measurements", label="a-data", unit="ma",
                         preset_data=np.NaN * np.ones((x_dim, y_dim)))


writer = MongoDataSetIOWriter(name='experiment_42')

data_set = DataSet(storage_writer=writer, name='experiment_42', data_arrays=measurements)

for i in range(x_dim):
    line = [i + j * random.random() for j in range(y_dim)]
    data_set.add_data(i, {'measurements': line})
    sleep(0.5)

data_set.finalize()
```

##### B
```python
import matplotlib.pyplot as plt

from qilib.data_set import MongoDataSetIOReader


plt.ion()

consumer_data_set = MongoDataSetIOReader.load(name='experiment_42')

fig, ax = plt.subplots()

while not consumer_data_set.is_finalized:
    consumer_data_set.sync_from_storage(0)
    ax.imshow(consumer_data_set.measurements, cmap='hot', interpolation='nearest')
    fig.canvas.draw()

```
