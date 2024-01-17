To start the magabot we run: 
$ roslaunch magabot magabot.launch

Now we need to create a path, for which we can open rviz to ping positions so that in the console we see the values for the initial and desired position. In path_planner we can change the values for goal and init.

This will write a path for our magabot to follow which can be seen in rviz.

For our robot to follow the path we must initialize the path_tracker.
