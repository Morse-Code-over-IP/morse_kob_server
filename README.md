
# KOBServer Software

## Installation
Create a new folder, KOBServer, on your hard drive.
Download KOBServer.py and save it in the KOBServer folder.
Download KOBServer.batch and save it in the KOBServer folder as KOBServer.bat.
Download pins.py and save it in the KOBServer folder.


## Configuration
You'll need to create a "web documents" folder containing a file named info.html. This is a static web page that KOB users can display by clicking on the "Server info" link at the bottom of the KOB activity page. Its main purpose is to identify the particular server currently in use by the KOB system. It can optionally provide other information as well.

Create a new folder, C:\www, on your hard drive. (With Linux, I've been using /var/www.)
Download the info file template info.html and save it in the C:\www folder.
Create a subfolder, logs, in the C:www folder.
Right-click on the C:\www\info.html file and select "Open with" > Notepad.
Edit the portions of the template that apply to your server. In particular, replace both instances of XX with your office call. Save the file when you're done.
Double-click on the info.html file to display it in your web browser and confirm that it looks the way you want.
Initial test
Open your KOBServer folder.
Double-click on the KOBServer.bat batch file (not the KOBServer.py Python file). This starts up the KOBServer program in a command prompt window.* (To launch the program in Linux, the command is python KOBServer.py /var/www.)
Stop the KOB server by closing the command prompt window.
Open KOBServer\errlog.txt and confirm that it contains a time stamp followed by the version number of the KOBServer program.
Open the C:\www folder and verify that the activity page, index.html, has been created. Double-click on this file to view it in your web browser.
Check the C:\www\logs folder and verify that the server log, log.html, has been created. Double-click to view its contents.
*If the command prompt window appears briefly and then immediately disappears, check the KOBServer\errlog.txt file for any error messages.

Autostart
You'll want KOBServer to launch itself automatically whenever you reboot your computer and have it run continuously in the background. One way to do this is to add a shortcut to the KOBServer.bat file to the Windows Startup folder.

Open the KOBServer folder, right-click on KOBServer.bat, and select Send To > Desktop. This creates a shortcut to KOBServer on the desktop.
Right-click on the desktop shortcut icon and select Properties. On the Shortcut tab, for the Run option select Minimized. Click OK.
Click on Start > All Programs, right-click on Startup, and select Open all users. This opens the Startup window on your screen.
Drag (or cut and paste) the KOBServer shortcut from the desktop to the Startup window.
Reboot the computer.
Verify that KOBServer has been successfully launched by opening the KOBServer folder and confirming that a new "Started KOBServer" entry has been added to the errlog.txt file. You should also see a KOBServer icon on the Windows task bar.


# References
- https://sites.google.com/site/morsekob/server/installation/software


# morse_kob_server
