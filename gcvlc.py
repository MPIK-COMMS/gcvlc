'''
(*)~----------------------------------------------------------------------------------
 Gaze-Controlled VLC Plugin for Pupil Labs Capture
 
 Author: Jonas Ditz
 Date: 21. September 2017
----------------------------------------------------------------------------------~(*)
'''

#import cv2
#import numpy as np
#import os
import sys
from pyglui import ui
from glfw import *

from plugin import Plugin
# logging
import logging
logger = logging.getLogger(__name__)

import myvlc


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
        
        self.menu = None
        
    def init_gui(self):
        # lets make a menu entry in the sidebar
        self.menu = ui.Growing_Menu('GCvlc Player')
        # add a button to close the plugin
        self.menu.append(ui.Button('Close', self.close))
        # add info text
        self.menu.append(ui.Info_Text('This Plugin creates a VLC Player instance that can be controlled by the User via Gaze. Look at the video to play it. The Player will pause automatically, if the User looks away.'))
        # add a text field to specify a video file
        self.menu.append(ui.Text_Input('video_file', self, setter=self.set_video_file, label='Video file'))
        # add a text field to specify the surface
        self.menu.append(ui.Text_Input('surface_name', self, setter=self.set_surface_name, label='Surface name'))
        # add button to resolve the stream
        self.menu.append(ui.Button('Start GCvlc Player', self.start_gcvlc_player))
        self.g_pool.sidebar.append(self.menu)
        
    def deinit_gui(self):
        if self.menu:
            self.g_pool.sidebar.remove(self.menu)
            self.menu = None

    def on_notify(self, notification):
        """Handels notifications
        
        Reacts to notification:
            No reactions to notifications implemented
        """
        pass

    def close(self):
        self.vlc.stop()
        self.alive = False
    
    def recent_events(self, events):
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
        self.deinit_gui()

    def set_video_file(self, value):
        self.video_file = value
        
    def set_surface_name(self,  value):
        self.surface_name = value
        
    def start_gcvlc_player(self):
            self.vlc.open_file(self.video_file)
            self.player_running = True
        
        
