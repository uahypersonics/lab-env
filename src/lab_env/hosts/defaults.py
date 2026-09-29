"""Hosts shared by all lab-env users."""

from lab_env.hosts.models import HostConfig

DEFAULT_HOSTS = {
    "uahpc": HostConfig(
        destination="hpc.arizona.edu",
        description="University of Arizona HPC",
        transfer_destination="filexfer.hpc.arizona.edu",
    ),
}
