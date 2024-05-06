import time
from datetime import datetime
import csv
from multiprocessing import Process
from signal import pause

from loguru import logger

def record_camera(timestamp: str):
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

    logger.debug(f"Starting recorgind {timestamp}...")
    picam2.start_recording(encoder, f'{timestamp}-video.mjpeg', pts=f'{timestamp}-video.timestamp.txt')
    try:
        pause()
    finally:
        logger.debug("Stopping recording...")
        picam2.stop_recording()

def record_imu_sensor(timestamp: str):
    from mpu6050 import mpu6050

    MPU_ADDR = 0x68
    sensor = mpu6050(MPU_ADDR)

    with open(f'{timestamp}-mpu.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["timestamp", "temp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"])

        while True:
            timestamp = datetime.now().isoformat()
            [accel, gyro, temp] = sensor.get_all_data()
            csvwriter.writerow([timestamp, temp, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']])
    
if __name__ == '__main__':
    from gpiozero import LED, Button
    timestamp = datetime.now().isoformat()
    logger.add(f'{timestamp}.log')
    p_camera = Process(target=record_camera, args=(timestamp,), daemon=True)
    p_imu = Process(target=record_imu_sensor, args=(timestamp,), daemon=True)

    button = Button(26, hold_time=5)

    def start():
        logger.debug("start")
        p_camera.start()
        p_imu.start()

    def terminate():
        logger.debug("end")
        try:
            p_imu.terminate()
        except AttributeError:
            pass
        try:
            p_camera.terminate()
        except AttributeError:
            pass
        
    button.when_held = start
    button.when_released = terminate

    pause()

