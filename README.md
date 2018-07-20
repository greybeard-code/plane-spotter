# plane-spotter
Python scrips to pull history from dump1080 ADB-S and summarize planes that are close to your location

## Installation
Setup your Rasperry Pi or computer with dump1090. Use the Mutability version of dump1090. https://github.com/mutability/dump1090
Or use the full installer at https://www.adsbreceiver.net/, it has a easy installer for mutability's version. The current values are the default install with ADBSreciever.

Once the sysem is setup and you've verified this working, install Plane-spotter.
Plane-spotter uses additional python libraries: json, yaml, math, time, glob. Most are built-in but you
will need to install yaml ` sudo apt-get install python-yaml`

Put the two Python scripts in the Pi user home or use git clone.

Edit the crontab of the root user to add both scripts (must be run as root)
```
  sudo crontab -e -u root
```
 - plane-spotter.py, every hour, 10 minutes after the hour (1:10, 2:20, 3:10, etc)
 - plane-spotter-weekly, once a week on Monday morning at 1:25 am

Add to the bottom of the crontab and save:
```
# PlaneSpotter
10 * * * * python /home/pi/plane_spotter.py
25 1 * * 1 python /home/pi/plane_spotter_weekly.py
```
Create a reports directory in your html directory and give the dump1090 user permission to create files there. If you're not using ADBSreceiver, use your html directory.
```
sudo mkdir /var/www/html/plane-spotter/
sudo chmod 766  /var/www/html/plane-spotter/

```
If you're not using ADBSreciever, edit both scripts to change the html reports directory that you created above and the location of the dump1090 json data files.

Edit the plane_spotter.py script with your GPS location and your desired range in kilometers. Find your GPS coordinates
on this website: https://gps-coordinates.org/

Once the crontab job runs (10 after), the report directory is ready to view. open a web browser, go to your dump1090 box and add /plane-spotter/ to the URL.
For example - http://192.168.1.34/plane-spotter/

## Future Development
1. Separate user input to a config.ini file
2. pretty up the tables with CSS code
3. Add a installer script
4. Add alert system that sends a email when conditions are met
