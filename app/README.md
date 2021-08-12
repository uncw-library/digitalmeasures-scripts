## Digital Measure (DM) to Turtle for Vivo

A turtle file contains all the DM user data that we wish to import into Vivo.  A single turtle file holds all the users.

### How to use it (non-docker approach):

install python3, lxml, selenium, and geckodriver

from a python3 venv:
 
 ```
 pip install -r requirements.txt
 python3 xml_to_turtle.py
 ```

it will ask for your DM password.

### How to use it (docker approach):

- create a file digitalmeasures-scripts/.env with contents:

```
DMUSER=changeme
DMPASS=changeme
```

```bash
docker-compose up --build
# script is not running yet.  The container is prepped & ready to run.
# I usually start another terminal & leave this current one running in the background.
# run inside container xml-to-turtle the program `python3 xml_to_turtle.py`: 
docker-compose exec xml-to-turtle python3 xml_to_turtle.py
```

Wait for 20 minutes for it to finish.

To stop the python script: `docker-compose down` and `docker-compose up`

To revise the app, (python script must be stopped, container can be running). `docker-compose up`  Then revise any file in the app/ folder, and rerun the `docker-compose exec xml-to-turtle python3 xml_to_turtle.py` command.

I like to comment out the function `hard_reset()` in xml_to_turtle.py after one successful run.  Otherwise, the app is designed to delete all the data you pulled from digital-measures and then repull all that data.  Pulling the data is the slowest step.  Remember to uncomment it before pushing to production, as the process requires a hard reset of the old data in order to pull in the latest data from digital-measures.


The output folder includes:

    excluded_users\
        DM files for users we are currently excluding
    included_users\
        DM files for users we are currently including
    profile_images\
        placeholder for when we implement photo feature
    parsed_users\
        human-readable files for each user.  parsed DM files
    turtles\
        turtle files created by xml_to_turtle.  Each turtle file is a complete Vivo dataset.  Only one should be imported into Vivo.  The filename includes creation date, to help identify the most recent one.  The latest output is userdata.ttl
    users\
        all DM files, both those we are including and those we are excluding.
    
#### Tips

- To manually replace User data in Vivo to a more recent turtle file:
    - Newer method:
        - Place the latest userdata.ttl file in the Vivo program at vivo/home/rdf/abox/filegraph/
        - Restart vivo (E.g., restart its tomcat)

    - Old method:
        - Get the current Vivo user data
            - navigate to the Site Admin page in a Vivo
            - click the "RDF Export" link
            - select "All Instance Data" and "Select Format: Turtle"
            - (this downloads the current user data to your computer)
        - Remove the current Vivo user data
            - return to the Site Admin page
            - click the "Add/Remove RDF Data" link
            - "Choose File" and choose the turtle file you just downloaded
            - click "Remove mixed RDF", choose "Turtle", and "Submit"
            - (wait as Vivo removes the current user data)
        - Import the new user data turtle file
            - return to the Site Admin page
            - click the "Add/Remove RDF Data" link
            - "Choose File" and choose the new turtle file
            - cleck "Add instace data", choose "Turtle", and "Submit"
            - (wait as Vivo adds the new user data)

- Profile_images complication:
    - app/profile_images must be shared to the Vivo instance
    - The puzzle is:
        xml_to_turtle.py needs to know which persons have a profile image.
        because it assigns FileNodes to those with photos.
        Those without a photo must have no FileNode, in order for Vivo to give the default image.
        By having the profile_photos in app/profile_photos, xml_to_turtle.py can give the correct items a FileNode.
        However, all of these photos in app/profile_photos must be then synced to the vivo server or dev box.
        Doing this in a painless manner is valuable.

