from datetime import datetime
from multiprocessing import Process

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

# Based on https://github.com/raspberrypi/picamera2/blob/main/examples/capture_video.py
def record_raw(timestamp: str):
    from picamera2 import MappedArray, Picamera2
    from picamera2.encoders import H264Encoder
    import cv2

    picam2 = Picamera2()
    video_config = picam2.create_video_configuration({"size": (1280, 720)})
    picam2.pre_callback = apply_timestamp
    picam2.configure(video_config)

    encoder = H264Encoder(10000000)

    picam2.start_recording(encoder, f'{timestamp}-video.h264', pts=f'{timestamp}-video-timestamp.txt')

def record_sensor(timestamp: str):
    from mpu6050 import mpu6050

    MPU_ADDR = 0x68
    sensor = mpu6050(MPU_ADDR)

    with open(f'{timestamp}-mpu.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        spamwriter.writerow(["temp", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"])

        while True:
            [accel, gyro, temp] = sensor.get_all_data()
            spamwriter.writerow([temp, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']])
    
if __name__ == '__main__':
    timestamp = datetime.now().isoformat()
    p = Process(target=record_raw(), args=(timestamp,))
    p.start()

    p.join()
