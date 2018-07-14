# plane-spotter
Python scrips to pull history from dump1080 ADB-S and summarize planes that are close to your location

## Installation

Put the two Pyhton scripts in the Pi user home or use git clone.

Edit the crontab of the dump1090 user to add both scripts
```
  sudo crontab -e -u dump1090
```
 - plane-spotter.py, every hour, 10 minutes after the hour (1:10, 2:20, 3:10, etc)
 - plane-spotter-weekly, once a week on Monday morning at 1:25 am 

Add to the bottom of the crontab and save:
```
# PlaneSpotter 
10 * * * * python /home/pi/plane_spotter.py
25 1 * * 1 python /home/pi/plane_spotter_weekly.py
```

Edit both scripts to set the html directory for reports and the location of the dump1090 
json data files. The current values are the default install with https://www.adsbreceiver.net/

Edit the main script with your GPS location and your desired range. Find your GPS coordinates
on this website: https://gps-coordinates.org/
 
## Future Development
1. Separate user input to a config.ini file
2. pretty up the tables with CSS code
3. Add a installer script
4. Add alert system that sends a email when conditions are met
