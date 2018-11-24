# RemoteNFS

This charm is built to connect a Juju charm to a non-Juju NFS server

## Usage

```
juju deploy ubuntu
juju deploy remote-nfs --config "nfs-server=my.nfs.server" --config "nfs-target=/nfs/share/path" --config "local-target=/local/share/path"
juju add-relation ubuntu remote-nfs
```