# Zanshin Add-on for Splunk

> The **Zanshin Add-on for Splunk** import Zanshin Alerts into Splunk.

## Requirements

* DOCKER

## How to use
Basic guide to start Splunk app with Zanshin Add-on installed in local environment.

### Start Splunk
```bash
make splunk-up
```
After finish you can open [http://localhost:8000/](http://localhost:8000/) in your browser.

### Stop Splunk
```bash
make splunk-down
```
After finish the address [http://localhost:8000/](http://localhost:8000/) will no longer be available.

### Clean Splunk
```bash
make splunk-clean
```
Will clean all Docker Splunk images in yout environment.

### Splunk Update
```bash
make splunk-update
```
This command will update the Add-on in the Splunk container and restart it, it is useful during development.

### Logs
```bash
make splunk-logs
make splunk-log-alerts
make splunk-log-following-alerts
```
Log commands are used to view the Splunk and Add-on logs in the console.

### Add-on Inspect
```bash
make splunk-inspect
```
This command is used to validate the quality of Splunk Add-on against a set of Splunk-defined criteria to determine whether the Add-on is ready for production and meets a minimum level of quality.

### Add-on package
```bash
make splunk-package
```
Will create an Add-on SPL file, ready to install on Splunk.

# TODO

* Finalize the Add-on README that will show in Splunk Base details page.
* Finalize this README

# FAQ
* Got permission denied while trying to connect to the Docker. 
    ```bash
    daemon socket at unix:///var/run/docker.sock
    groups
    groupadd docker
    sudo usermod -aG docker $USER
    reboot
    ```
