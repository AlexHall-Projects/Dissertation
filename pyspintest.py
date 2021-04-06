from simple_pyspin import Camera
import time
from PIL import Image
import os

def image_capture(duration):

    num_frames = int(duration*50)

    with Camera() as cam:
        # If this is a color camera, request the data in RGB format.
        if 'Bayer' in cam.PixelFormat:
            cam.PixelFormat = "RGB8"

        # Get images from the full sensor
        cam.OffsetX = 0
        cam.OffsetY = 0
        cam.Width = cam.SensorWidth
        cam.Height = cam.SensorHeight

        #set framerate
#        cam.AcquisitionFrameRate = 60

        print('Opened camera: %s (#%s)' % (cam.DeviceModelName, cam.DeviceSerialNumber))

        print('Recording...')

        # Start recording
        cam.start()
        start = time.time()
        print(start)

        # Get 100 images as numpy arrays
        imgs = [cam.get_array() for n in range(num_frames)]

        # Stop recording
        el = time.time() - start
        print('el is', el)
        cam.stop()

    print('Acquired %d images in %.2f s (~ %.1f fps)' % (len(imgs), el, len(imgs)/el))

    # Make a directory to save some images
    output_dir = 'test_images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print('Saving to "%s"' % output_dir)

    # Save them
    for n, img in enumerate(imgs):
        Image.fromarray(img).save(os.path.join(output_dir, '%08d.jpg' % n))

    return start