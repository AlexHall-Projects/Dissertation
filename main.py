import sys #import relevant modules, importing a module 'as' will require its acronym
from PyQt5 import QtWidgets as qtw #prefix for any of the modules funtions
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimediaWidgets as qtmw
from PyQt5 import QtMultimedia as qtmm
#from simple_pyspin import Camera
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
        "configure main window"
        self.resize(qtc.QSize(1000, 600)) #size of application on opening
        self.setWindowTitle('Eye Tracker GUI') #set title
        self.setWindowIcon(qtg.QIcon('eye2.jpg')) #set window icon
        base_widget = qtw.QWidget()
        base_widget.setLayout(qtw.QHBoxLayout()) #box layout places widgets auto right to left and top to bottom

        "configure tab widget"
        notebook = qtw.QTabWidget() #adds tab widget that will contain video and camera viewfinder
        notebook.setMinimumSize(400, 200) #sets minimum size in case user resizes window
        base_widget.layout().addWidget(notebook) #add the notebook as a widget to the base widget layout

        "configure video file viewer"
        self.file_list = qtw.QListWidget() #create widget for video file viewer
        self.file_list.setFixedSize(300,100) #sets fixed size of file viewer
        base_widget.layout().addWidget(self.file_list) #adds the file viewer to the base widget

        self.setCentralWidget(base_widget) #set base widget as central widget, without this widget will not be visible

        "status bar"
        self.status_bar = qtw.QStatusBar() #setup status bar
        self.setStatusBar(self.status_bar)#appending with 'self' enables object globally

        "menu bar"
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        #video_folder = menu_bar.addMenu('Video folder')
        support_menu = menu_bar.addMenu('Support')
        video_folder = file_menu.addAction('Video folder')
        video_folder.triggered.connect(self.vid_file)
        image_folder = file_menu.addAction('Image folder')
        image_folder.triggered.connect(self.img_file)
        help = support_menu.addAction('Help')
        help.triggered.connect(self.help)


        "Video play controls"
        toolbar = self.addToolBar("Video & Camera Controls") #create toolbar named video & camera controls
        play_action = toolbar.addAction('Play') #add play button
        play_icon = self.style().standardIcon(qtw.QStyle.SP_MediaPlay) #assign play icon.
        play_action.setIcon(play_icon) #link play icon to play action
        pause_action = toolbar.addAction('Pause') #add pause button
        stop_action = toolbar.addAction('Stop') #add stop button
        self.addToolBar(qtc.Qt.BottomToolBarArea, toolbar) #toolbar defaults to bottom of page
        toolbar.setMovable(False) #toolbar cannot be moved
        toolbar.setFloatable(False) #toolbar cannot float

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
        #play_action.triggered.connect(self.player.play)
        play_action.triggered.connect(self.test_control)
        #play_action.triggered.connect(self.pyspin_grabber)
        #play_action.triggered.connect(self.imgacq)
        pause_action.triggered.connect(self.player.pause)
        stop_action.triggered.connect(self.player.stop)

        # end main UI code
        self.show()

    "function integrating the video playback and camera control --heart of program--"
    def test_control(self):
        self.statusBar().showMessage('Acquiring and saving images, please wait.', 5000) #no idea where this doesn't show up
        timer1 = time.time() #get time of video starting
        self.player.play() #play video
        import pyspintest
        
        ret_value = pyspintest.image_capture(self.duration) #call image capture script and assign its return value
        print(ret_value) #for dev purposes only
        self.cam_lag = float(ret_value - timer1) #compute lag time of camera
        self.test_concluded_msg(self.cam_lag) #update status bar message

    "function test concluded status message"
    def test_concluded_msg(self, cam_lag):
        self.statusBar().showMessage('Test completed, camera lag time: %.2f seconds' % cam_lag) #had to break out
        #into seperate function due to status bar buggy output

    "function for viewing the video files"
    def vid_file(self):
        os.system('explorer.exe "C:\\Users\\ajh-1\\Video_file"') #explorer opens on documents rather than given file path, unsure why.

    "fucntion for viewing the image files"
    def img_file(self):
        os.system('explorer.exe "C:\\Users\\ajh-1\\OneDrive\\Documents\\Dissertation\\test_images"')#also doesn't open correct path, permissions?

    "function to control links to support docs --support docs yet to be written--"
    def help(self): #link to support docs in here
        pass

    "refresh the video file list to ensure it's up to date"
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

    "set the video file selected by the user for the test"
    def on_file_selected(self, item):
        fn = item.text()
        url = qtc.QUrl.fromLocalFile(self.video_dir.filePath(fn))
        content = qtmm.QMediaContent(url)
        self.player.setMedia(content)

    "Function to calculate duration of video, this is required for camera control"
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
        duration = float(frames/fps) #compute frames/fps for total duration in seconds
        print("Duration of video is:", duration) #print for test purposes only.
        self.status_bar.showMessage('Duration of video is %.2f seconds.' % duration)
        self.duration = duration
        return duration


if __name__ == '__main__': # only runs code if scripts is called directly
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())



