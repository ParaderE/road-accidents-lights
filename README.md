# Road accident detector

## Preparation

Install requirement libraries from `requirements.txt` with 
```bash
pip install -r requirements.txt
```
Run the `setup.py` script to prepare config files
Then you are ready to start

## Creating service

Create a "/etc/systemd/system/accidents.service" file and paste following code
```
[Service]  
Type=simple  
Restart=always  
RestartSec=1  
User=centos
ExecStart=/path/to/python /path/to/dir/daemon.py start
```

## Running service on boot

To enable running on boot
```bash
sudo systemctl enable --now accidents
```
---