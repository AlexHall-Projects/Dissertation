import sys #import relevant modules, importing a module 'as' will require its acronym
from PyQt5 import QtWidgets as qtw #prefix for any of the modules funtions
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimediaWidgets as qtmw
from PyQt5 import QtMultimedia as qtmm
from simple_pyspin import Camera
import cv2
import time
from PIL import Image
import os
from multiprocessing import Process


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        "MainWindow constructor"
        super().__init__()
        # main UI code goes here
        self.resize(qtc.QSize(1000, 600)) #size of application on opening
        base_widget = qtw.QWidget()
        base_widget.setLayout(qtw.QHBoxLayout()) #box layout places widgets auto right to left and top to bottom
        notebook = qtw.QTabWidget() #adds tab widget that will contain video and camera viewfinder
        notebook.setMinimumSize(400, 200) #sets minimum size in case user resizes window
        base_widget.layout().addWidget(notebook) #add the notebook as a widget to the base widget layout
        self.file_list = qtw.QListWidget() #create widget for video file viewer
        self.file_list.setFixedSize(300,100) #sets fixed size of file viewer
        base_widget.layout().addWidget(self.file_list) #adds the file viewer to the base widget
        self.setCentralWidget(base_widget) #set base widget as central widget, without this widget will not be visible

        "Video play controls"
        toolbar = self.addToolBar("Video & Camera Controls") #create toolbar named video & camera controls
        play_action = toolbar.addAction('Play') #add play button
        pause_action = toolbar.addAction('Pause') #add pause button
        stop_action = toolbar.addAction('Stop') #add stop button

        "Get program to make a file with specific name unless it already exists"
        self.video_dir = qtc.QDir.home()
        if not self.video_dir.cd('Video_file'):
            qtc.QDir.home().mkdir('Video_file')
            self.video_dir.cd('Video_file') #make video_dir point to new file

        "setup videoplayer widget"
        self.player = qtmm.QMediaPlayer()
        self.video_widget = qtmw.QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self.refresh_video_list()  # call video list refresh function
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.itemClicked.connect(
            lambda: notebook.setCurrentWidget(self.video_widget)
        )
        self.file_list.itemClicked.connect(self.capture_duration) #link selected video to video duration function.

        "Add video widget to GUI"
        notebook.addTab(self.video_widget, "Video")
        play_action.triggered.connect(self.player.play)
        play_action.triggered.connect(self.pyspin_grabber)
        #play_action.triggered.connect(self.imgacq)
        pause_action.triggered.connect(self.player.pause)
        stop_action.triggered.connect(self.player.stop)

        # end main UI code
        self.show()

    #######################
    ## video file viewer ##
    #######################
    #def videoplay(self):
    #    self.player.play()

    #def onclick(self):
    #    p1 = Process(target=self.imgacq)
    #    p2 = Process(target=self.videoplay)
    #    p1.start()
    #    p2.start()
    #    p1.join()
    #    p2.join()

    def refresh_video_list(self):
        self.file_list.clear()
        video_files = self.video_dir.entryList(
            ["*.ogg", "*.avi", "*.mov", "*.mp4", "*.mkv"],#ISSUE1: will only accept avi files
            qtc.QDir.Files | qtc.QDir.Readable
        )
        for fn in sorted(video_files):
            self.file_list.addItem(fn)

    ###########################################
    ### link file selection to video player ###
    ###########################################

    def on_file_selected(self, item):
        fn = item.text()
        url = qtc.QUrl.fromLocalFile(self.video_dir.filePath(fn))
        content = qtmm.QMediaContent(url)
        self.player.setMedia(content)

    def capture_duration(self, item):#recieves file list item from file_list
        fn = item.text() #extract text data of file, ie file name
        url = qtc.QUrl.fromLocalFile(self.video_dir.filePath(fn)) #get URL of file
        print(url) #unforunately PyQt5 doesn't give a clean file path to hand to openCV
        url = url.toString() #convert 'URL' to string
        url.strip("PyQt5.QtCore.QUrl('/") #strip string of everything before the C.
        print(url) #print for testing only
        data = cv2.VideoCapture(url) #start video capture with openCV
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT) #get number of frames of video
        fps = int(data.get(cv2.CAP_PROP_FPS)) #get fps of video
        duration = int(frames/fps) #compute frames/fps for total duration in seconds
        print("Duration of video is:", duration) #print for test purposes only.
        self.duration = duration
        return duration

    def pyspin_grabber(self):
        import pyspintest
        pyspintest.image_capture(self.duration)

    # def imgacq(self):#FPS of camera averages 54FPS
    #     duration = self.duration
    #     print('Duration is', duration
    #     num_frames = (duration*60) #duration of video in seconds multiplied by recording frame rate of camera.
    #     print(num_frames)
    #     with Camera() as cam:
    #         if 'Bayer' in cam.PixelFormat:
    #             cam.PixelFormat = 'RGB8'
    #
    #     cam.OffsetX = 0
    #     cam.OffsetY = 0
    #     cam.Width = cam.SensorWidth
    #     cam.Height = cam.SensorHeight
    #
    #     self.statusBar().showMessage('Opened camera %s (#%s), now recording...' % (cam.DeviceModelName, cam.DeviceSerialNumber))
    #     cam.start()
    #     start = time.time()
    #
    #     imgs = [cam.get_array() for n in range(num_frames)] #num frames must = number of frames in selected video.
    #
    #     el = time.time() - start
    #     cam.stop()
    #
    #     print('Acquired %d images in %.2f s (~ %.1f fps)' % (len(imgs), el, len(imgs) / el))
    #
    #     # Make a directory to save some images
    #     output_dir = 'test_images'
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
    #
    #     print('Saving to "%s"' % output_dir)
    #
    #     # Save them
    #     for n, img in enumerate(imgs):
    #         Image.fromarray(img).save(os.path.join(output_dir, '%08d.jpg' % n))

if __name__ == '__main__': # only runs code if scripts is called directly
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())



