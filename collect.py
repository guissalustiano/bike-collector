import time
from datetime import datetime
import csv
from multiprocessing import Process
from signal import pause
from pathlib import Path

from loguru import logger

def record_camera(basepath: Path):
    from picamera2 import MappedArray, Picamera2
    from picamera2.encoders import JpegEncoder
    import cv2

    def apply_timestamp(
        request,
        colour = (0, 255, 0),
        origin = (0, 30),
        font = cv2.FONT_HERSHEY_SIMPLEX,
        scale = 1,
        thickness = 2,
    ):
        timestamp = datetime.now().isoformat()
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)

    # Setup camera
    picam2 = Picamera2()
    picam2.pre_callback = apply_timestamp # add timestamp on top left
    video_config = picam2.create_video_configuration({"size": (1280, 720)})
    picam2.configure(video_config)

    encoder = JpegEncoder(q=70)

    logger.debug(f"Starting recorgind {basepath}...")
    picam2.start_recording(encoder, (basepath / "video.mjpeg").as_posix(), pts=(basepath / "video_timestamp.txt").as_posix())
    try:
        pause()
    finally:
        logger.debug("Stopping recording...")
        picam2.stop_recording()

def record_imu_sensor(basepath: Path):
    from mpu6050 import mpu6050

    MPU_ADDR = 0x68
    logger.debug(f"Starting MPU {basepath}...")
    sensor = mpu6050(MPU_ADDR)

    with open(basepath / "mpu.csv", 'w', buffering=1) as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["timestamp", "temp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"])

        while True:
            timestamp = datetime.now().isoformat()
            [accel, gyro, temp] = sensor.get_all_data()
            csvwriter.writerow([timestamp, temp, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']])

def record_gps(basepath: Path):
    from serial import Serial
    from pyubx2 import UBXReader

    def maybe_getattribute(obj, property: str):
        if hasattr(obj, property):
            return obj.__getattribute__(property)
        else:
            return None

    with open(basepath / "gps.csv", 'w', buffering=1) as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["time",
                            "date",
                            "lat",
                            "lon",
                            "alt",
                            "altUnit",
                            "sep",
                            "sepUnit",
                            "identity",
                            "navStatus",
                            "posMode",
                            "spd",
                            "status",
                            "talker",
                            "numSV"
                        ])

        with Serial('/dev/ttyACM0', 9600, timeout=3) as stream:
            ubr = UBXReader(stream, protfilter=1)
            for _, p in ubr:
                if hasattr(p, "time") and hasattr(p, "lat") and hasattr(p, "lon") :
                    csvwriter.writerow([
                       p.time,
                       maybe_getattribute(p, "date"),
                       p.lat,
                       p.lon,
                       maybe_getattribute(p, "alt"),
                       maybe_getattribute(p, "altUnit"),
                       maybe_getattribute(p, "sep"),
                       maybe_getattribute(p, "sepUnit"),
                       maybe_getattribute(p, "identity"),
                       maybe_getattribute(p, "navStatus"),
                       maybe_getattribute(p, "posMode"),
                       maybe_getattribute(p, "spd"),
                       maybe_getattribute(p, "status"),
                       maybe_getattribute(p, "talker"),
                       maybe_getattribute(p, "numSV"),
                   ])
    
if __name__ == '__main__':
    from gpiozero import LED, Button

    timestamp = datetime.now().timestamp()
    basepath = Path(str(timestamp))

    logger.add(basepath / f'exec.log')
    p_camera = None
    p_imu = None
    p_gps = None

    button = Button(26, hold_time=5)

    def start():
        logger.debug("start")
        p_camera = Process(target=record_camera, args=(basepath,))
        p_imu = Process(target=record_imu_sensor, args=(basepath,))
        p_gps = Process(target=record_gps, args=(basepath,))
        p_camera.start()
        p_imu.start()
        p_gps.start()

    def terminate():
        logger.debug("end")
        try:
            p_imu.terminate()
        except AttributeError:
            pass
        try:
            p_gps.terminate()
        except AttributeError:
            pass
        try:
            p_camera.terminate()
        except AttributeError:
            pass
        
    #button.when_held = start
    #button.when_released = terminate
    start()

    pause()

