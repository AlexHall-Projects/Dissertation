from simple_pyspin import Camera
import time
from PIL import Image
import os
from multiprocessing import Process


def image_capture(duration):
    global fps
    # duration = int(input('enter duration')) #dev purposes only

    if 0 < duration <= 5:
        fps = 30
    if 5 < duration <= 10:
        fps = 30
    if 10 < duration <= 15:
        fps = 30
    if 15 < duration <= 20:
        fps = 31
    if 20 < duration <= 30:
        fps = 32
    if duration > 30:
        fps = 25

    print(fps)
    num_frames = int(duration * fps)

    # Make a directory to save some images
    output_dir = 'test_images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with Camera() as cam:
        # If this is a color camera, request the data in RGB format.
        if 'Bayer' in cam.PixelFormat:
            cam.PixelFormat = "RGB8"

        # Get images from the full sensor
        cam.OffsetX = 0
        cam.OffsetY = 0
        cam.Width = cam.SensorWidth
        cam.Height = cam.SensorHeight

        # cam.AcquisitionFrameRateAuto = 'Off'
        # cam.AcquisitionFrameRateEnabled = True
        # cam.AcquisitionFrameRate = 32

        print('Opened camera: %s (#%s)' % (cam.DeviceModelName, cam.DeviceSerialNumber))

        print('Recording...')

        # Start recording
        cam.start()
        start = time.time()
        # print(start)

        for a in range(num_frames):
            imgs = [cam.get_array() for n in range(1)]
            for n, img in enumerate(imgs):
                Image.fromarray(img).save(os.path.join(output_dir, '%08d.jpg' % a))

        # Stop recording
        el = time.time() - start
        # print('el is', el)
        cam.stop()

    print('Acquired %d images in %.2f s (~ %.1f fps)' % (num_frames, el, num_frames / el))
    # print('Acquired %d images in %.2f s (~ %.1f fps)' % (len(img), el, len(img) / el))

    # Make a directory to save some images
    # output_dir = 'test_images'
    # if not os.path.exists(output_dir):
    #    os.makedirs(output_dir)

    # print('Saving to "%s"' % output_dir)

    # Save them
    # for n, img in enumerate(imgs):
    #    Image.fromarray(img).save(os.path.join(output_dir, '%08d.jpg' % n))

    return start


p1 = Process(target=image_capture)
p1.start()
p1.join()
