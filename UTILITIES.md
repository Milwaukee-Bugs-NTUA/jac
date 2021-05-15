# Basic jac commands

JAC shell offers 9 commands 

## ▶️ join

Node joins chord cluster.
```
jac-cli@ntua$ join --help
Usage: join [OPTIONS]

  Inserts a new node.

Options:
  -b, --bootstrap-node <ip> <port>
                                  Specify bootstrap node of chord
  -h, --help                      Show this message and exit.
```

## 📥 insert

Inserts new key-value pair inside chord.
```
jac-cli@ntua$ insert --help
Usage: insert [OPTIONS] <key> <value>

  Inserts the pair (<key>, <value>).

Options:
  -h, --help  Show this message and exit.
```

## 📤 query

Searchs a specified key and returns its value.
```
jac-cli@ntua$ query --help
Usage: query [OPTIONS] <key>

  Finds the value of <key>.

Options:
  -h, --help  Show this message and exit.
```
## 🗑️ delete

Deletes specified key-value pair.
```
jac-cli@ntua$ delete --help
Usage: delete [OPTIONS] <key>

  Deletes the specified <key>.

Options:
  -h, --help  Show this message and exit.
```

## ⏸️ depart

Removes current node from chord. Server is not stopped for future usage.
```
jac-cli@ntua$ depart --help
Usage: depart [OPTIONS]

  Makes current node to depart.

Options:
  -h, --help  Show this message and exit.
```

## 📖 overlay

Shows nodes of cluster. Current node is colored green.
```
jac-cli@ntua$ overlay --help
Usage: overlay [OPTIONS]

  Displays current network topology.

Options:
  -h, --help  Show this message and exit.
```

## 🔍 info

Shows information about current node like ip, port, hash key and stored keys inside the node.
```
jac-cli@ntua$ info --help
Usage: info [OPTIONS]

  Displays info for current node.

Options:
  -h, --help  Show this message and exit.
```

## 🆘 help

Shows a help message.
```
jac-cli@ntua$ help -h
Usage: help [OPTIONS]

  Prints a help message for all jac commands.

Options:
  -h, --help  Show this message and exit.
```

## ❌ exit

Node is removed from the cluster, server is stopped and the jac shell is terminated. This command calls ``depart`` command.
