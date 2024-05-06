# Basic record data on raspberry

## Hardware
- Raspberry Pi 4B
- PiCam
- MPU6050 connected to the I2C
- uBloxGPS connected by USB
- a switch or equivalent connected between GND and GPIO26

## Install
### 1. Download the code
#### By git
```bash
git clone https://github.com/guissalustiano/bike-collector.git
```

#### By zip file
```bash
cd ~/Documents/ # or any folder that you want to download the project
wget https://github.com/guissalustiano/bike-collector/archive/refs/heads/main.zip
unzip main.zip
mv bike-collector-main/ bike-collector/
cd bike-collector
```

###  2. Create a python virtual env
Inside the folder that you downloaded, run:
```bash
python3 -m venv --system-site-packages .venv
```

Every time that you access a new shell to run the project you need
to activate the environment with:
```bash
source .venv/bin/activate
```

To deactivate the python environment run
```bash
deactivate
```

You can find more information [here](https://docs.python.org/3/library/venv.html).

### 3. Install dependencies
First, install Picamera and SMBus on the system.
```bash
sudo apt install -y python3-picamera
sudo apt install -y python3-smbus
```

Then install the extra python packages.
```bash
pip install -r requirements.txt
```

## Run
Change the variable `PATH` with the python code directory (`pwd`), 
then run the script as a normal python code.
```bash
python collect.py
```
It will wait until the switch is held for 5 seconds (to avoid bounce) to start the record, and when the switch is released the record is stopped immediately to start the record, 
and when the switch is released the record is stopped immediately.

### Automatic start of the script on startup
Usually, you don't have access to the rpi console when you make the measures,
so it's useful to config the program to run on startup and restart automatically in case of error.

To do it, you need to config a systemmd service and enable it.

First change the directory on the `collector.service`.
```bash
sudo cp collector.service /etc/systemd/system/bike-collector.service
sudo systemctl daemon-reload
sudo systemctl enable bike-collector.service

# Check if it is running
systemctl status bike-collector.service
```

## Reading the data
### Move data to your computer
You can use the rpi UI or do it by the command line with `scp`.

### Reading the video frames
You can use `ffmeg` to extract the frames from the video (ex: `ffmpeg -i file:video.mjpeg video/frame%d.png`).
Then you need to check the timestamp on the first frame and from that you can use the `*.timestamp.txt` files to calculate the timestamp of the next frames.

### Reading the IMU data
The imu data is a simple csv with the following colluns:
- timestamp - YYYY-MM-DD HH:MM:SS:mmmmmm (iso format)
- temperature
- accelerometer X
- accelerometer Y
- accelerometer Z
- gyroscope X
- gyroscope Y
- gyroscope Z

## References
- [Virtual env for picamera2](https://forums.raspberrypi.com/viewtopic.php?t=361758)
- [Picamera examples](https://github.com/raspberrypi/picamera2/tree/main/examples)
- [Picamera manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
