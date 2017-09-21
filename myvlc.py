'''
(*)~----------------------------------------------------------------------------------
 Wrapper class for VLC Python API
 
 Author: Jonas Ditz
 Date: 21. September 2017
----------------------------------------------------------------------------------~(*)
'''

import vlc


class VLC:
    def __init__(self):
        """A simple Media Player using VLC
        """
        # creating a basic vlc instance
        self.instance = vlc.Instance("--no-xlib")
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        
    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
        else:
            if self.mediaplayer.play() == -1:
                return
            self.mediaplayer.play()
            
    def play(self):
        """Play player
        """
        if self.mediaplayer.is_playing():
            return
        self.mediaplayer.play()
    
    def pause(self):
        """Pause player 
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
    
    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        
    def open_file(self, filename = None):
        """Open a video file and load it into the Media Player
        """
        if filename == None:
            return
        
        # create the media
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        
    def set_volume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)
