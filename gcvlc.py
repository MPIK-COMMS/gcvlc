'''
(*)~----------------------------------------------------------------------------------
 Gaze-Controlled VLC Plugin for Pupil Labs Capture
 
 Author: Jonas Ditz
 Date: 21. September 2017
----------------------------------------------------------------------------------~(*)
'''

import numpy as np
import sys
from pyglui import ui
from pyglui.cygl.utils import Named_Texture
from glfw import *
from gl_utils import *
import OpenGL.GL as gl
from platform import system
from plugin import Plugin

# logging
import logging
logger = logging.getLogger(__name__)

import myvlc


# window callbacks: resize window
def on_resize(window, w, h):
    active_window = glfwGetCurrentContext()
    glfwMakeContextCurrent(window)
    adjust_gl_view(w,h)
    glfwMakeContextCurrent(active_window)
    
# generate marker matrix
def generate_marker(marker):
    n = 10
    if marker == 'first':
        mat = np.array([[0, 0, 0, 0, 0, 0, 0], [0, 255, 255, 255, 255, 255, 0], [0, 255, 0, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 255, 255, 255, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 0, 0, 0, 0, 0, 0]],  np.uint8)
        res = np.kron(mat, np.ones((n, n)))
        return res.astype(np.uint8)
    elif marker == 'second':
        mat = np.array([[0, 0, 0, 0, 0, 0, 0], [0, 255, 255, 255, 255, 255, 0], [0, 255, 0, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 0, 255, 0], [0, 255, 255, 255, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 0, 0, 0, 0, 0, 0]],  np.uint8)
        res = np.kron(mat, np.ones((n, n)))
        return res.astype(np.uint8)
    elif marker == 'third':
        mat = np.array([[0, 0, 0, 0, 0, 0, 0], [0, 255, 255, 255, 255, 255, 0], [0, 255, 0, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 255, 255, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 0, 0, 0, 0, 0, 0]],  np.uint8)
        res = np.kron(mat, np.ones((n, n)))
        return res.astype(np.uint8)
    elif marker == 'fouth':
        mat = np.array([[0, 0, 0, 0, 0, 0, 0], [0, 255, 255, 255, 255, 255, 0], [0, 255, 0, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 0, 255, 0], [0, 255, 255, 0, 0, 255, 0], 
                        [0, 255, 255, 255, 255, 255, 0], [0, 0, 0, 0, 0, 0, 0]],  np.uint8)
        res = np.kron(mat, np.ones((n, n)))
        return res.astype(np.uint8)
 

class GCvlc_Player(Plugin):
    """This Plugin creates a gaze-controlled VLC-Player.
    """
    def __init__(self, g_pool, video_file='/hdd/jonas/Gaze-Controlled_VLC_Player/test_input/test.mp4'):
        super().__init__(g_pool)
        # order (0-1) determines if your plugin should run before other plugins or after
        self.order = .7

        # name of the LSL stream and output file
        self.video_file = video_file
        
        # create vlc player object
        self.vlc = myvlc.VLC()
        
        # variable to determine whether the player is running
        self.player_running = False
        
        # surface that contains the vlc player
        self.surface_name = "Screen1"
        
        # window to display marker
        self._window = None
        
        # specify marker and marker scale
        self.marker1 = np.load('/home/jonas/pupil_capture_settings/plugins/marker/marker1.npy')
        self.marker1 = self.marker1.astype(np.uint8)
        self.marker2 = np.load('/home/jonas/pupil_capture_settings/plugins/marker/marker2.npy')
        self.marker2 = self.marker2.astype(np.uint8)
        self.marker3 = np.load('/home/jonas/pupil_capture_settings/plugins/marker/marker3.npy')
        self.marker3 = self.marker3.astype(np.uint8)
        self.marker4 = np.load('/home/jonas/pupil_capture_settings/plugins/marker/marker4.npy')
        self.marker4 = self.marker4.astype(np.uint8)
        self.m_size = 200.0
        
        self.menu = None
        
        # UI Platform tweaks
        if system() == 'Linux':
            self.window_position_default = (0, 0)
        elif system() == 'Windows':
            self.window_position_default = (8, 31)
        else:
            self.window_position_default = (0, 0)
        
    def init_ui(self):
        try:
            # lets make a menu entry in the sidebar
            self.add_menu()
            # add a label to the menu
            self.menu.label = 'GCvlc Player'
            # add info text
            self.menu.append(ui.Info_Text('This Plugin creates a VLC Player instance that can be controlled by the User via Gaze. Look at the video to play it. The Player will pause automatically, if the User looks away.'))
            # add a text field to specify a video file
            self.menu.append(ui.Text_Input('video_file', self, setter=self.set_video_file, label='Video file:'))
            # add a text field to specify the surface
            self.menu.append(ui.Text_Input('surface_name', self, setter=self.set_surface_name, label='Surface name:'))
            # add slider to change marker size
            self.menu.append(ui.Slider('m_size',  self, 
                             label='Marker size [pixels]', 
                             min=1,  max=500, step=1))
            # add button to start the VLC player
            self.menu.append(ui.Button('Start GCvlc Player', self.start_gcvlc_player))
            #self.g_pool.sidebar.append(self.menu)
            
            # open new window for the VLC player
            self.open_window('GCVLC_MarkerScreen')
        except:
            logger.error("Unexpected error: {}".format(sys.exc_info()))
        
    def deinit_ui(self):
#        if self.menu:
#            self.g_pool.sidebar.remove(self.menu)
#            self.menu = None
        self.remove_menu()
            
    def open_window(self, title='new_window'):
        try:
            width, height = 1280, 720
            self._window = glfwCreateWindow(width, height, title, share=glfwGetCurrentContext())
            glfwSetWindowPos(self._window, self.window_position_default[0], self.window_position_default[1])
            
            # bind vlc player to glfw window
            if system() == 'Windows':
                self.vlc.mediaplayer.set_hwnd(glfwGetWindowUserPointer(self._window))
            else:
                self.vlc.mediaplayer.set_xwindow(glfwGetWindowUserPointer(self._window))
            
            # Register callbacks
            glfwSetFramebufferSizeCallback(self._window, on_resize)
            on_resize(self._window, *glfwGetFramebufferSize(self._window))
            
            # gl_state settings
            active_window = glfwGetCurrentContext()
            glfwMakeContextCurrent(self._window)
            basic_gl_setup()
            # refresh speed settings
            glfwSwapInterval(0)

            glfwMakeContextCurrent(active_window)
        except:
            logger.error("Unexpected error: {}".format(sys.exc_info()))
            
    def close_window(self):
        if self._window:
            # enable mouse display
            active_window = glfwGetCurrentContext()
            glfwSetInputMode(self._window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)
            glfwDestroyWindow(self._window)
            self._window = None
            glfwMakeContextCurrent(active_window)
            
    def gl_display_in_window(self):
        try:
            active_window = glfwGetCurrentContext()
            if glfwWindowShouldClose(self._window):
                self.close_window()
                return
                
            # make plugin window current context and clear the screen
            glfwMakeContextCurrent(self._window)
            clear_gl_screen()
            
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            p_window_size = glfwGetFramebufferSize(self._window)
            gl.glOrtho(0, p_window_size[0], p_window_size[1], 0, -1, 1)
            # Switch back to Model View Matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # draw markers
            m1 = Named_Texture()
            m1.update_from_ndarray(self.marker1)
            m1.draw(True, ((1.0, self.m_size), (self.m_size, self.m_size), (self.m_size, 1.0), (1.0, 1.0)), 1.0)
            
            m2 = Named_Texture()
            m2.update_from_ndarray(self.marker2)
            m2.draw(True, ((p_window_size[0]-self.m_size, self.m_size), (p_window_size[0]-1.0, self.m_size), (p_window_size[0]-1.0, 1.0), (p_window_size[0]-self.m_size, 1.0)), 1.0)
            
            m3 = Named_Texture()
            m3.update_from_ndarray(self.marker3)
            m3.draw(True, ((1.0, p_window_size[1]-1.0), (self.m_size, p_window_size[1]-1.0), (self.m_size, p_window_size[1]-self.m_size), (1.0, p_window_size[1]-self.m_size)), 1.0)
            
            m4 = Named_Texture()
            m4.update_from_ndarray(self.marker4)
            m4.draw(True, ((p_window_size[0]-self.m_size, p_window_size[1]-1.0), (p_window_size[0]-1.0, p_window_size[1]-1.0), (p_window_size[0]-1.0, p_window_size[1]-self.m_size), (p_window_size[0]-self.m_size, p_window_size[1]-self.m_size)), 1.0)
            
            # swap buffer
            glfwSwapBuffers(self._window)
            glfwMakeContextCurrent(active_window)
        except:
            logger.error("Unexpected error: {}".format(sys.exc_info()))

    def on_notify(self, notification):
        """Handels notifications
        
        Reacts to notification:
            No reactions to notifications implemented
        """
        pass
    
    def recent_events(self, events):
        if self._window:
            self.gl_display_in_window()
        
        if not self.player_running:
            return
            
        try:
            surfaces = events.get('surfaces')
            if not surfaces:
                self.vlc.pause()
                return
            
            # iterate over all detected surfaces
            aux_not_srf = True
            for s in surfaces:
                # check whether the surface contains the vlc player
                if s['name'] == self.surface_name:
                    aux_not_srf = False
                    # play the video if the gaze lies on the surface, pause otherwise
                    if s['gaze_on_srf'][0]['on_srf'] == True:
                        self.vlc.play()
                    else:
                        self.vlc.pause()
            
            # if the needed surface is not tracked, pause the video
            if aux_not_srf:
                self.vlc.pause()
        except:
            logger.error("Unexpected error: {}".format(sys.exc_info()))

    def get_init_dict(self):
        # anything vars we want to be persistent accross sessions need to show up in the __init__
        # and identically as a dict entry below:
        return {'video_file': self.video_file}

    def cleanup(self):
        """ called when the plugin gets terminated.
        This happens either voluntarily or forced.
        if you have a GUI or glfw window destroy it here.
        """
        self.vlc.stop()
        self.close_window()
        self.deinit_ui()

    def set_video_file(self, value):
        self.video_file = value
        
    def set_surface_name(self, value):
        self.surface_name = value
        
    def start_gcvlc_player(self):
        self.vlc.open_file(self.video_file)
        self.vlc.play()
        self.player_running = True
