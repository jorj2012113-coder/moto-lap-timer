#!/usr/bin/env python3
"""
Motorcycle Lap Timer - Helmet Camera Edition
Uses optical flow and marker detection to track lap times from helmet camera footage
"""

import cv2
import numpy as np
import time
from collections import deque
from datetime import datetime

class HelmetLapTimer:
    def __init__(self, video_path=None, marker_color_hsv_lower=(0, 100, 100), 
                 marker_color_hsv_upper=(10, 255, 255), smoothing_window=10):
        """
        Initialize the lap timer
        
        Args:
            video_path: Path to video file (None for webcam)
            marker_color_hsv_lower: HSV lower bound for track marker (default: red)
            marker_color_hsv_upper: HSV upper bound for track marker
            smoothing_window: Window size for position smoothing
        """
        self.video_path = video_path
        self.marker_lower = marker_color_hsv_lower
        self.marker_upper = marker_color_hsv_upper
        self.smoothing_window = smoothing_window
        
        # State tracking
        self.lap_times = []
        self.position_history = deque(maxlen=smoothing_window)
        self.last_crossing_time = None
        self.frame_count = 0
        self.fps = 30
        self.prev_gray = None
        self.crossed_marker = False
        
        # Statistics
        self.session_start = datetime.now()
        
    def detect_marker(self, frame):
        """
        Detect track marker (red/colored line) in frame using color detection
        Returns: center point of detected marker or None
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.marker_lower, self.marker_upper)
        
        # Morphological operations to clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > 100:  # Minimum area threshold
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy), largest_contour
        
        return None, None
    
    def detect_motion_peaks(self, frame, prev_frame):
        """
        Detect high motion areas (approaching/passing marker) using optical flow
        Returns: average motion magnitude
        """
        if prev_frame is None:
            return 0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        return np.mean(mag)
    
    def smooth_position(self, pos):
        """
        Smooth position using moving average to reduce jitter
        """
        if pos is not None:
            self.position_history.append(pos)
        
        if len(self.position_history) > 0:
            avg_x = np.mean([p[0] for p in self.position_history])
            avg_y = np.mean([p[1] for p in self.position_history])
            return (int(avg_x), int(avg_y))
        return None
    
    def check_crossing(self, marker_pos, motion_magnitude, frame_width):
        """
        Determine if a lap crossing has occurred
        Logic: marker near center + high motion = crossing event
        """
        if marker_pos is None:
            self.crossed_marker = False
            return False
        
        center_region_left = frame_width * 0.35
        center_region_right = frame_width * 0.65
        
        # Check if marker is in center region (rider approaching/crossing)
        in_center = center_region_left < marker_pos[0] < center_region_right
        
        # High motion indicates fast approach
        high_motion = motion_magnitude > 2.0
        
        # Crossing detected: marker in center + motion + wasn't just crossed
        if in_center and high_motion and not self.crossed_marker:
            self.crossed_marker = True
            return True
        elif not in_center or motion_magnitude < 1.0:
            self.crossed_marker = False
        
        return False
    
    def record_lap(self, current_time):
        """
        Record a lap crossing and calculate lap time
        """
        if self.last_crossing_time is None:
            # First crossing - just set the reference
            self.last_crossing_time = current_time
            return None
        
        lap_time = current_time - self.last_crossing_time
        self.lap_times.append(lap_time)
        self.last_crossing_time = current_time
        
        return lap_time
    
    def process_video(self):
        """
        Main processing loop for video file or webcam
        """
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
        else:
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print(f"Error: Could not open video source: {self.video_path}")
            return
        
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        if self.fps == 0:
            self.fps = 30
        
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Starting lap timer...")
        print(f"Video: {frame_width}x{frame_height} @ {self.fps} FPS")
        print(f"Press 'q' to quit, 'r' to reset, 's' to save stats")
        print("\n" + "="*50)
        
        prev_frame = None
        
        while True:
            ret, frame = cap.read()]
            if not ret:
                print("\nEnd of video reached.")
                break
            
            self.frame_count += 1
            current_time = self.frame_count / self.fps
            
            # Detect marker
            marker_pos, marker_contour = self.detect_marker(frame)
            
            # Smooth position
            smoothed_pos = self.smooth_position(marker_pos)
            
            # Detect motion
            motion = self.detect_motion_peaks(frame, prev_frame)
            
            # Check for crossing
            if self.check_crossing(smoothed_pos, motion, frame_width):
                lap_time = self.record_lap(current_time)
                if lap_time is not None:
                    print(f"\n🏁 LAP {len(self.lap_times)}: {lap_time:.2f}s")
                else:
                    print(f"\n🏁 START/REFERENCE POINT SET")
            
            # Draw visualization
            frame_display = frame.copy()
            
            # Draw center region
            cv2.rectangle(frame_display, 
                         (int(frame_width * 0.35), 0),
                         (int(frame_width * 0.65), frame_height),
                         (255, 255, 0), 2)
            
            # Draw detected marker
            if smoothed_pos:
                cv2.circle(frame_display, smoothed_pos, 15, (0, 255, 0), 3)
                cv2.putText(frame_display, "MARKER", (smoothed_pos[0] - 30, smoothed_pos[1] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            if marker_contour is not None:
                cv2.drawContours(frame_display, [marker_contour], 0, (0, 200, 0), 2)
            
            # Display stats
            cv2.putText(frame_display, f"Frame: {self.frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame_display, f"Time: {current_time:.2f}s", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame_display, f"Motion: {motion:.2f}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if len(self.lap_times) > 0:
                cv2.putText(frame_display, f"Laps: {len(self.lap_times)}", (10, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                last_lap = self.lap_times[-1]
                cv2.putText(frame_display, f"Last: {last_lap:.2f}s", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Helmet Lap Timer", frame_display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset()
                print("\n" + "="*50)
                print("Session reset.")
            elif key == ord('s'):
                self.save_stats()
            
            prev_frame = frame
        
        cap.release()
        cv2.destroyAllWindows()
        self.print_summary()
    
    def reset(self):
        """
        Reset session data
        """
        self.lap_times = []
        self.last_crossing_time = None
        self.frame_count = 0
        self.session_start = datetime.now()
    
    def print_summary(self):
        """
        Print session summary statistics
        """
        print("\n" + "="*50)
        print("SESSION SUMMARY")
        print("="*50)
        
        if len(self.lap_times) == 0:
            print("No laps recorded.")
            return
        
        print(f"Total Laps: {len(self.lap_times)}")
        print(f"\nLap Times:")
        for i, lap_time in enumerate(self.lap_times, 1):
            print(f"  Lap {i}: {lap_time:.2f}s")
        
        avg_lap = np.mean(self.lap_times)
        min_lap = np.min(self.lap_times)
        max_lap = np.max(self.lap_times)
        
        print(f"\nStatistics:")
        print(f"  Average: {avg_lap:.2f}s")
        print(f"  Fastest: {min_lap:.2f}s")
        print(f"  Slowest: {max_lap:.2f}s")
        print(f"  Std Dev: {np.std(self.lap_times):.2f}s")
        
        total_time = np.sum(self.lap_times)
        print(f"  Total Time: {total_time:.2f}s ({total_time/60:.1f}m)")
        print("\n" + "="*50)
    
    def save_stats(self):
        """
        Save lap times to CSV file
        """
        if len(self.lap_times) == 0:
            print("No laps to save.")
            return
        
        filename = f"lap_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w') as f:
            f.write("Lap,Time(s)\n")
            for i, lap_time in enumerate(self.lap_times, 1):
                f.write(f"{i},{lap_time:.2f}\n")
            
            # Add statistics
            f.write(f"\nStatistics\n")
            f.write(f"Average,{np.mean(self.lap_times):.2f}\n")
            f.write(f"Min,{np.min(self.lap_times):.2f}\n")
            f.write(f"Max,{np.max(self.lap_times):.2f}\n")
            f.write(f"Std Dev,{np.std(self.lap_times):.2f}\n")
        
        print(f"Stats saved to: {filename}")


if __name__ == "__main__":
    import sys
    
    video_file = None
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    
    # Create timer with red marker detection (adjust HSV values for your marker color)
    # Red in HSV: H: 0-10 or 170-180, S: 100-255, V: 100-255
    timer = HelmetLapTimer(
        video_path=video_file,
        marker_color_hsv_lower=(0, 100, 100),
        marker_color_hsv_upper=(10, 255, 255),
        smoothing_window=10
    )
    
    timer.process_video()
