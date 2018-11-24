from charms.reactive import when, when_any, when_not, set_flag
import charms.apt
# import charmhelpers.core.fstab as fstab
import charmhelpers.core.hookenv as hookenv
import charmhelpers.core.host as host


@when_not('nfs.installed')
def install_remote_nfs():
    charms.apt.queue_install(['nfs-common'])
    set_flag('nfs.installed')

@when('nfs.installed')
@when_any(
      'config.changed.nfs-server',
      'config.changed.nfs-target',
      'config.changed.local-target')
def setup_mount():
    config = hookenv.config()
    new_server = config.get('nfs-server')
    new_target = config.get('nfs-target')
    new_path = config.get('local-target')
    hookenv.log("About to check for {} / {} / {}".format(new_server, new_target, new_path))
    if not (new_server and new_target and new_path):
        missing = "Missing required configuration: "
        if not new_server:
            missing += "new_server, "
        if not new_target:
            missing += "new_target, "
        if not new_path:
            missing += "new_path, "
        hookenv.status_set('blocked', missing)
        return
    hookenv.log("Setting up NFS share - {}:{} -> {}".format(new_server, new_target, new_path))
    old_server = config.previous('nfs-server')
    old_target= config.previous('nfs-target')
    old_path = config.previous('local-target')
    if old_path:
        hookenv.log("About to unmount {}".format(
            old_path))
        try:
            unmount(old_path)
        except:
            pass
        try:
            host.fstab_remove(old_path)
        except:
            pass
    hookenv.log("About to mount {}:{} at {}".format(
        new_server, new_target, new_path))

    host.fstab_add(
        "{}:{}".format(new_server, new_target),
        new_path,
        "nfs",
        options="auto,nofail,noatime,nolock,intr,tcp,actimeo=1800"
        )
    host.mkdir(new_path)
    host.fstab_mount(new_path)
    hookenv.status_set('active', "{}:{} -> {}".format(new_server, new_target, new_path))
