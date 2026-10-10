#!/usr/bin/env python3
"""
Example usage of the Helmet Lap Timer with different configurations
"""

from helmet_lap_timer import HelmetLapTimer


def example_red_marker():
    """
    Example: Red track marker detection (most common)
    """
    print("Starting lap timer with RED marker detection...")
    
    timer = HelmetLapTimer(
        video_path="track_video.mp4",
        marker_color_hsv_lower=(0, 100, 100),
        marker_color_hsv_upper=(10, 255, 255),
        smoothing_window=10
    )
    
    timer.process_video()


def example_white_marker():
    """
    Example: White track marker detection
    """
    print("Starting lap timer with WHITE marker detection...")
    
    timer = HelmetLapTimer(
        video_path="track_video.mp4",
        marker_color_hsv_lower=(0, 0, 200),
        marker_color_hsv_upper=(180, 20, 255),
        smoothing_window=12
    )
    
    timer.process_video()


def example_green_marker():
    """
    Example: Green track marker detection
    """
    print("Starting lap timer with GREEN marker detection...")
    
    timer = HelmetLapTimer(
        video_path="track_video.mp4",
        marker_color_hsv_lower=(40, 40, 40),
        marker_color_hsv_upper=(80, 255, 255),
        smoothing_window=10
    )
    
    timer.process_video()


def example_webcam_live():
    """
    Example: Live webcam feed (test in real-time)
    """
    print("Starting lap timer with LIVE WEBCAM...")
    print("Note: You'll need a marker near the camera for testing")
    
    timer = HelmetLapTimer(
        video_path=None,  # None = use webcam
        marker_color_hsv_lower=(0, 100, 100),
        marker_color_hsv_upper=(10, 255, 255),
        smoothing_window=10
    )
    
    timer.process_video()


def example_high_sensitivity():
    """
    Example: More sensitive detection (catches more laps but more false positives)
    """
    print("Starting lap timer with HIGH SENSITIVITY...")
    
    timer = HelmetLapTimer(
        video_path="track_video.mp4",
        marker_color_hsv_lower=(0, 80, 80),     # Lower S/V thresholds
        marker_color_hsv_upper=(20, 255, 255),  # Wider range
        smoothing_window=5                      # Less smoothing = faster response
    )
    
    timer.process_video()


def example_low_sensitivity():
    """
    Example: Less sensitive detection (fewer false positives but might miss some laps)
    """
    print("Starting lap timer with LOW SENSITIVITY...")
    
    timer = HelmetLapTimer(
        video_path="track_video.mp4",
        marker_color_hsv_lower=(0, 120, 120),   # Higher S/V thresholds
        marker_color_hsv_upper=(8, 255, 255),   # Narrower range
        smoothing_window=15                     # More smoothing = more stable
    )
    
    timer.process_video()


if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    # example_red_marker()
    # example_white_marker()
    # example_green_marker()
    # example_webcam_live()
    # example_high_sensitivity()
    example_low_sensitivity()
