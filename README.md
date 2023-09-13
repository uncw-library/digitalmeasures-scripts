## Digital Measures XML to Vivo Turtle for Import

Python venv:  Setting up a venv is a tricky part of python development.  A python venv contains your python dependencies so that you don't pollute your system python with weird packages.  If you use Anaconda or Conda, then they automatically start a python venv (good thing).  Otherwise you'll have to create/start one manually.  I recommend Anaconda or Miniconda or Conda for python dev, because it does this tricky part automatically.

#### Commands

with a ./vivo-data-update/.env and a geckodriver (described below)
`python3 app/xml_to_turtle.py`

Flags:
  - help 
  --no_reset  (prevents reset of local dm folder.)

i.e., `python3 app/xml_to_turtle.py --no_reset` will skip the DM data pull & use the previously pulled DM data.  This saves a ton of time during dev work.


#### Folders

- app/
    python code for creating a turtle file from DigitalMeasures (DM) repo
- output/
    non-git-committed folder for the output of app/xml_to_turtle.py
    output/turtles/userdata.ttl is the Vivo datafile
    output/users/ is the raw xml data from digitalmeasures WatermarkFacultySuccess
    output/parsed_users/ is json of output/users with only the useful info retained
    output/person_images/ is a nested folder of profile photos as vivo expects the folder nesting


#### Files that support all approaches

- requirements.txt
    `pip install -r requirement.txt` installs the python packages

#### Files only used in the docker build (optional):

- crontab
    docker uses this to schedule what time to rerun the xml_to_turtle
- docker-compose.yml
    if you prefer not installing python, you can run the app via `docker-compose up`
    warning: there are complications with this.  See app notes.
    After the container is up, in another terminal run `docker-compose exec vivo-data-update python3 xml_to_turtle.py --no_reset`
- docker-compose-production.yml
    a schema for running the app on Rancher 1.x
- Dockerfile

#### Non-git-commited files

- .env
```
DM_API_PASS=CHANGEME
DM_SAMBA_USER=CHANGEME
DM_SAMBA_PASS=CHANGEME
DM_PHOTO_FOLDER=CHANGEME
JOBLOG_DB_HOST=CHANGEME
JOBLOG_DB_USER=CHANGEME
JOBLOG_DB_PASS=CHANGEME
APP_ENV=production (or anything else == dev env)
```

- geckodriver app.  Each OS installs this differently.  You'll need to search the web for this download and install it.

### Rancher-based production:

The userdata.ttl file is volume mounted onto the host filesystem.  The vivo container volume mounts that same file into its abox/filegraph/ path.  On Vivo restart, vivo autoimports the new userdata.ttl. 

The person_images folder created by this app is also docker volume mounted onto the host filesystem.  The docker vivo container volume mounts that same folder into the expected filepath in Vivo app.  That filepath autoloads into Vivo on Vivo restart

```
docker build --no-cache --platform linux/amd86 -t libapps-admin.uncw.edu:8000/randall-dev/vivo-data-update .
docker push libapps-admin.uncw.edu:8000/randall-dev/vivo-data-update
```

### Bare-metal production:

``sudo crontab -e`` contains the following lines:

```
# fetch data from digitalmeasures, write output to userfile.ttl, copy file to vivo, restart vivo
0 23 * * * python3 /usr/local/vivo-data-update/app/xml_to_turtle.py
0 0 * * * rsync -avz --chown=tomcat:tomcat /usr/local/vivo-data-update/output/turtles/userdata.ttl /usr/local/VIVO/home/rdf/abox/filegraph/userdata.ttl
0 0 * * * rsync -avz --chown=tomcat:tomcat /usr/local/vivo-data-update/output/person_images /usr/local/VIVO/home/uploads/filestorage_root/
10 0 * * * /bin/systemctl restart tomcat
```
