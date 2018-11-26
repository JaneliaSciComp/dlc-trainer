Cyvasse

This project implements a cron job that runs on
login1.int.janelia.org.  It monitors a folder (usually named something
like /something/something/cyvasse-drop) for video files, and when it
finds them it runs compresses them using ffmpeg (and the HEVC codec),
placing the output .mp4 file in a parallel location, typically named
something like

    /something/something/cyvasse-drop-output .

Before installing Cyvasse, you should figure out what user the cronjob
will run as, and then do the build while logged in as that user.

Next, create a file named "configuration" that points to the folders
you want to use for input and output.  See configuration-svoboda for
an example.

Next, if you have no jobs in your current crontab that you want to
keep, do

    ./turn-on

to add the cyvasse-launching line to the crontab file.  (You can
delete this line with the ./turn-off bash script.)

After this, the contents of the input folder should automatically get
processed every 5 minutes.

ALT
2018-11-24


