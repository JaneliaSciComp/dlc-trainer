DLC Trainer

This project is based on the DeepLabCut project:

https://github.com/AlexEMG/DeepLabCut

All the code under the dlc folder is the original DeepLabCut code, and
therefore carries its own copyright and license (GPLv3).

This project implements a cron job that runs on
login1.int.janelia.org.  It monitors a folder (usually named something
like /something/something/dlc-trainer-drop) for targets folders, and
when it finds them it uses DeepLabCut to train a model on the targets.
It outputs a "model folder" containing the model in a parallel
location, typically named something like

    /something/something/dlc-trainer-drop-output .

Before installing DLC Trainer, you should figure out what user the
cronjob will run as, and then do the build while logged in as that
user.

Before building DLC Trainer, you should figure out what user the
cronjob will run as, and then do the build while logged in as that
user.

To build, you first need to build the Singularity image within which
DeepLabCut runs.  To do this, you need a linux box with root
privleges, and with Singularity installed (as of this writing, I last
used an Ubuntu 18.04.1 box).  Do this to build the image:

    sudo singularity build dlc.simg dlc.def

(Make sure you delete any old image named dlc.simg, or else
singularity will complain.)  After this completes, you may want to
chown/chmod dlc.simg to make it owned by you, and have normal file
permissions.

Next, create a file named "configuration" that points to the folders
you want to use for input and output.  See configuration-svoboda for
an example.

Next, if you have no jobs in your current crontab that you want to
keep, do

    ./turn-on

to add the DLC-Trainer-launching line to the crontab file.  (You can
delete this line with the ./turn-off bash script.)

After this, the contents of the input folder should automatically get
processed every 5 minutes.

ALT
2018-11-27
