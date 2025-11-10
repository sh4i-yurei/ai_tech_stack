# SOP: Ubuntu Server Patching Steps

## Purpose
This SOP outlines the standard procedure for applying security and package updates to Ubuntu servers.

## Procedure

1.  **Connect to the server:**
    ```bash
    ssh username@your_ubuntu_server_ip
    ```
2.  **Update package lists:**
    ```bash
    sudo apt update
    ```
3.  **Upgrade installed packages:**
    ```bash
    sudo apt upgrade -y
    ```
4.  **Remove obsolete packages:**
    ```bash
    sudo apt autoremove -y
    ```
5.  **Reboot if necessary:**
    *   Check if a reboot is required: `cat /var/run/reboot-required`
    *   If the file exists, reboot the server: `sudo reboot`
6.  **Verify updates:** After reboot (if performed), reconnect and verify system health.
