This is a very simple build of a UPS simulator I made for a coding project.
It uses Python and MySQL to build a database and a simulation of air cargo transportation.

REQUIREMENTS: XAMPP, Python 3.0, mysql-connector-python

1. You first must have XAMPP installed and have Apache and MySQL running. 

2. You must run setup_db.py to generate the database. (note, by default the db access is user=root, password=)

3. Run the generation scripts, this ensures you have a full fleet, airports, and ULDs in your database

4. Run either gui_main.py for a user interface or main.py. Both work the same. You are able to view the manifest of each plane and see all the cans onboard, where they're going and how much they weigh.

BUGS: 

gui_main.py is a little janky, especially when you click on a can to view the manifest.

Sometimes planes won't load fully, sometimes they do. Just a logic issue I need to fix
