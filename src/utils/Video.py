import pygame
import cv2
import numpy as np
import threading
import time
import os

class Video:
    def __init__(self, video_path):
        """
        Initialize video player with a video file path.
        
        Args:
            video_path (str): Path to the video file
        """
        self.video_path = video_path
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.is_paused = False
        self.fps = 30
        self.frame_delay = 1.0 / self.fps
        self.last_frame_time = 0
        self.video_thread = None
        self.stop_flag = False
        
        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found at {video_path}")
            self.cap = None
            return
            
        # Initialize video capture
        try:
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                print(f"Error: Could not open video file {video_path}")
                self.cap = None
                return
                
            # Get video properties
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.frame_delay = 1.0 / self.fps
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video loaded: {video_path} - {self.width}x{self.height} @ {self.fps}fps")
            
        except Exception as e:
            print(f"Error initializing video {video_path}: {e}")
            self.cap = None
    
    def play(self):
        """Start playing the video"""
        if self.cap is None:
            return
            
        self.is_playing = True
        self.is_paused = False
        self.stop_flag = False
        
        # Start video thread if not already running
        if self.video_thread is None or not self.video_thread.is_alive():
            self.video_thread = threading.Thread(target=self._video_loop, daemon=True)
            self.video_thread.start()
    
    def pause(self):
        """Pause the video"""
        self.is_paused = True
    
    def resume(self):
        """Resume the video"""
        self.is_paused = False
    
    def stop(self):
        """Stop the video and reset to beginning"""
        self.is_playing = False
        self.is_paused = False
        self.stop_flag = True
        
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        
        # Wait for thread to finish
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=1.0)
    
    def _video_loop(self):
        """Main video playback loop (runs in separate thread)"""
        while self.is_playing and not self.stop_flag and self.cap:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            current_time = time.time()
            
            # Check if it's time for the next frame
            if current_time - self.last_frame_time >= self.frame_delay:
                ret, frame = self.cap.read()
                
                if ret:
                    # Convert BGR to RGB (OpenCV uses BGR, pygame uses RGB)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_frame = frame_rgb
                    self.last_frame_time = current_time
                else:
                    # End of video, loop back to beginning
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
            
            time.sleep(0.001)  # Small sleep to prevent busy waiting
    
    def get_current_frame(self):
        """Get the current frame as a numpy array"""
        return self.current_frame
    
    def draw(self, surface, rect):
        """
        Draw the current frame to a pygame surface within the specified rectangle.
        
        Args:
            surface: Pygame surface to draw on
            rect: Pygame rect defining the area to draw the video
        """
        if self.current_frame is None:
            return
            
        try:
            # Convert numpy array to pygame surface
            frame_surface = pygame.surfarray.make_surface(self.current_frame.swapaxes(0, 1))
            
            # Scale the frame to fit the rectangle
            scaled_frame = pygame.transform.scale(frame_surface, (rect.width, rect.height))
            
            # Draw the frame
            surface.blit(scaled_frame, rect)
            
        except Exception as e:
            print(f"Error drawing video frame: {e}")
    
    def get_info(self):
        """Get video information"""
        if self.cap is None:
            return None
            
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'total_frames': self.total_frames,
            'duration': self.total_frames / self.fps if self.fps > 0 else 0
        }
    
    def cleanup(self):
        """Clean up video resources"""
        self.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.current_frame = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class VideoManager:
    """Manager class for handling multiple videos"""
    
    def __init__(self):
        self.videos = {}
    
    def load_video(self, video_id, video_path):
        """Load a video with a given ID"""
        try:
            video = Video(video_path)
            self.videos[video_id] = video
            return video
        except Exception as e:
            print(f"Error loading video {video_id}: {e}")
            return None
    
    def get_video(self, video_id):
        """Get a video by ID"""
        return self.videos.get(video_id)
    
    def play_video(self, video_id):
        """Play a video by ID"""
        video = self.videos.get(video_id)
        if video:
            video.play()
    
    def stop_video(self, video_id):
        """Stop a video by ID"""
        video = self.videos.get(video_id)
        if video:
            video.stop()
    
    def stop_all_videos(self):
        """Stop all videos"""
        for video in self.videos.values():
            video.stop()
    
    def cleanup_all(self):
        """Clean up all videos"""
        for video in self.videos.values():
            video.cleanup()
        self.videos.clear()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup_all()


# Alternative simple video class if OpenCV is not available
class SimpleVideo:
    """Simplified video class that just shows a placeholder"""
    
    def __init__(self, video_path):
        self.video_path = video_path
        self.is_playing = False
        self.current_frame = None
        print(f"SimpleVideo: OpenCV not available, using placeholder for {video_path}")
    
    def play(self):
        self.is_playing = True
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def stop(self):
        self.is_playing = False
    
    def draw(self, surface, rect):
        # Draw a simple placeholder
        pygame.draw.rect(surface, (100, 100, 100), rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        
        # Add text
        font = pygame.font.Font(None, 24)
        text = font.render("Video Placeholder", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
    
    def cleanup(self):
        pass


# Try to use the full Video class, fall back to SimpleVideo if OpenCV is not available
try:
    import cv2
    # cv2 is available, use the full Video class
    pass
except ImportError:
    print("OpenCV (cv2) not found. Video playback will use placeholders.")
    # Replace Video class with SimpleVideo
    Video = SimpleVideo