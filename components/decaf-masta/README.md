# MaSta

This component provides functions to deploy and modify scenarios on the infrastructure.

## Start as daemon

First, source the environment and create packages as usual. Then simply run

```
mastad -c ./decaf_masta/components/config/masta.cfg
```

If you do not want to let it run as a daemon, you can also call

```
python -m tests.masta_daemon_test.py
```

## Kill the daemon

If you have had enough of the daemon, just call

```
kill `cat /var/run/decaf/mastad.pid` 
```