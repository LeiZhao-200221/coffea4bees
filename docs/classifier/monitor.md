# Monitor System

The monitor system consists of a central server that handles the aggregation and visualization of the data and multiple clients that send log, progress and other information to the server. For now, the visualization is limited to the console output provided by [`rich`](https://rich.readthedocs.io/en/stable/index.html) package.

In general, if you only run a local multiprocessing workflow that requires only one `./pyml.py` call for each step, you will not need to directly interact with the monitor system. A server will be started automatically by the main process, and all subprocesses will connect to the server.

If you use a distributed system or need to start multiple `./pyml.py` calls simultaneously on one or more machines, you may consider start a separate monitor server and connect all `./pyml.py` calls to that server.

## Manual Monitor Server

A server can be started by the command:

```bash
./pyml.py monitor -setting Monitor "address: :<port>"
```

where the `<port>` is a valid port number. If successful, the IP address and port will be printed to the console.

Then for all other `./pyml.py` calls, you need to add the following argument to connect to the server:

```bash
-setting Monitor "{address: <ip>:<port>, connect: true}"
```

where `<ip>` is the IP address of the server.

If you run everything on the same machine, you can use `localhost:<port>` as the address or any other string without the `:<port>` part which will be interpreted as a [`AF_UNIX`](https://docs.python.org/3/library/socket.html#socket.AF_UNIX) socket.

## Logging

When using the built-in `logging` module, all messages will automatically be redirected to the monitor server.

Comparing to the default behavior, the rendering is improved to support the following features seamlessly:

- multiple messages can be sent together in one call, e.g.

```python
logging.info("message1", "message2", "message3")
```

- the original formatting behavior is still valid, e.g.

```python
logging.info("message1 %s", "message2")
```

- `rich` objects are supported

```python
logging.info("title of table", rich.table.Table("col1", "col2"))
```

!!! warning

    Do not pass large objects (e.g. `torch.Tensor`) directly to logging, as all raw messages will be pickled and sent to the server for rendering. Instead, convert all large objects to strings or `rich` objects before logging.

## Progress

A progress tracker for a single threaded job can be used as follow:

```python

from classifier.monitor.progress import Progress

with Progress.new(total=100, msg=("step", "Message")) as progress:
    for i in range(100):
        progress.advance(1)
    # or
    for i in range(100):
        progress.update(i + 1)
```

For a multithreading/multiprocessing job, it is recommended to use `progress.advance` inside the done callback (e.g. use `add_done_callback(lambda _: progress.advance(1))`), which is more robust under connection instability.

If a progress tracker has to be shared by multiple processes, use `progress.advance` with `distributed=True`.

## Usage

The `Usage` will keep track of the CPU, memory and GPU usage for each process and record every second (configurable via `-setting monitor.Usage interval`). The data will be sent to the server only when a checkpoint is created. If the usage tracking is disabled, the checkpoint will do nothing and the overhead is negligible.

The checkpoints with messages can be created by the following code:

```python
from classifier.monitor.usage import Usage

for i in range(10):
    Usage.checkpoint("step", i)
```

By default, the usage tracking is disabled. Enable it by the argument:

```bash
-setting monitor.Usage "enable: true"
```

The data can be visualized by the argument:

```bash
-analysis monitor.Usage
```

where the usage from all processes will be stacked and the checkpoints will be visible as vertical bars.

!!! warning

    The resource tracking will use extra CPU and memory, so it is not recommended for production jobs.

## Tips

- Sometimes the printed IP address is incorrect especially when using containers. You may need to use `localhost` or `AF_UNIX` for local jobs or get the correct IP address from other tools.

- If the process exit unexpectedly without any error message, you may need to check if the `forward_exception` is disabled in `monitor.Log` setting. If not, you need to make sure that is disabled during debugging, as some of the fatal errors may kill the process immediately before the message is sent to the monitor server.

- During debugging, if some of the logs are not displayed, you may consider use `print` instead and not use multiprocessing.
