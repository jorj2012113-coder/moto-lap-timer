# Motorcycle Lap Timer - Helmet Camera Edition

A Python program that analyzes helmet camera footage to automatically detect and measure motorcycle lap times on a track.

## Features

✅ **Helmet Camera Optimized**: Designed for footage from an on-helmet camera  
✅ **Marker Detection**: Tracks a colored line/marker on the track (e.g., red paint, tape)  
✅ **Optical Flow Analysis**: Uses motion detection to identify lap crossings  
✅ **Automatic Lap Timing**: Records lap times from marker crossings  
✅ **Statistics**: Calculates average, fastest, and slowest laps  
✅ **Export CSV**: Saves lap data to a file for analysis  
✅ **Real-time Visualization**: Shows detection visualization during playback  

## How It Works

1. **Marker Detection**: The program detects a colored finish line marker (default: red) using HSV color space
2. **Motion Analysis**: Uses optical flow to detect when you're approaching the marker at speed
3. **Crossing Logic**: When the marker is centered in frame + high motion detected = lap recorded
4. **Smoothing**: Position history is smoothed to reduce false detections

## Setup

### Requirements
- Python 3.7+
- OpenCV
- NumPy
- SciPy

### Installation

```bash
git clone https://github.com/jorj2012113-coder/moto-lap-timer.git
cd moto-lap-timer
pip install -r requirements.txt
```

## Usage

### Process a Video File

```bash
python helmet_lap_timer.py path/to/video.mp4
```

### Use Webcam (Live)

```bash
python helmet_lap_timer.py
```

### Controls During Playback

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Reset session (clear lap times) |
| `s` | Save lap times to CSV |

## Customization

### Change Marker Color

Edit the HSV values in `helmet_lap_timer.py`:

```python
timer = HelmetLapTimer(
    video_path=video_file,
    marker_color_hsv_lower=(0, 100, 100),      # Adjust lower HSV
    marker_color_hsv_upper=(10, 255, 255),     # Adjust upper HSV
    smoothing_window=10
)
```

**Common HSV Ranges:**
- **Red**: `(0, 100, 100)` to `(10, 255, 255)` or `(170, 100, 100)` to `(180, 255, 255)`
- **Green**: `(40, 40, 40)` to `(80, 255, 255)`
- **Blue**: `(100, 100, 100)` to `(130, 255, 255)`
- **Yellow**: `(20, 100, 100)` to `(30, 255, 255)`
- **White**: `(0, 0, 200)` to `(180, 20, 255)`

### Adjust Detection Sensitivity

- **`smoothing_window`**: Larger = more stable but slower detection (default: 10)
- **Marker area threshold**: Line 73 - change `area > 100` to filter noise
- **Motion threshold**: Line 115 - change `motion_magnitude > 2.0` to be more/less sensitive

## Track Setup Tips

1. **Use a Clear Marker**: Paint a bright, high-contrast line at the start/finish (not too small)
2. **Lighting**: Ensure consistent lighting across laps
3. **Camera Position**: Mount helmet camera to capture the track ahead clearly
4. **Speed**: Approach the marker at reasonable speed for better detection
5. **Avoid Shadows**: Shadows can interfere with color detection

## Output Files

When you press `s` during playback or after quitting, lap times are saved to:

```
lap_times_YYYYMMDD_HHMMSS.csv
```

Example CSV output:
```
Lap,Time(s)
1,85.34
2,83.21
3,82.98
4,84.11

Statistics
Average,83.91
Min,82.98
Max,85.34
Std Dev,0.92
```

## Troubleshooting

**No laps detected?**
- Verify marker color HSV values match your track marker
- Ensure you're crossing the marker at reasonable speed
- Check video lighting and contrast
- Try adjusting the `motion_magnitude` threshold

**Too many false detections?**
- Increase `smoothing_window` (e.g., 15-20)
- Reduce motion sensitivity threshold
- Use a higher contrast marker

**Frame rate issues?**
- Lower video resolution
- Increase frame skip interval
- Check CPU usage

## Future Enhancements

- [ ] YOLO-based motorcycle detection
- [ ] Multi-rider tracking
- [ ] Graphical UI for marker calibration
- [ ] Race comparison analysis
- [ ] GPS speed overlay
- [ ] Thermal imaging support

## License

MIT License - Feel free to modify and use!

## Contributing

Feel free to submit issues and pull requests!
