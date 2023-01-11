## Digital Measures to Turtle

`python3 app/xml_to_turtle.py`

Flags:
  - help 
  --no_reset  (prevents reset of local dm folder.)

i.e., `python3 app/xml_to_turtle.py --no_reset` will skip the DM data pull & use the previously pulled DM data.  This saves a ton of time during dev work.


Python venv:  This is the hardest part of python development.  If you use Anaconda or Conda, then they automatically start a python venv (good thing).  Otherwise you'll have to create/start one manually.  Python venv manages your python dependencies so that you don't pollute your system python with weird packages. I recommend Anaconda or Miniconda or Conda for python dev, because it does this tricky part automatically.

#### Folders

- app/
    python code for creating a turtle file from DigitalMeasures (DM) repo
- experiments/
    jupyter notebooks for investigating the DM output
- output/
    non-git-committed folder holding output of app/xml_to_turtle.py
    output/turtles/userdata.ttl is the Vivo datafile

#### Files that support all approaches

- requirements.txt
    `pip install -r requirement.txt` installs the python packages

#### Files only used in the docker build (optional):

- crontab
    docker uses this to schedule what time to rerun the xml_to_turtle
- docker-compose.yml
    if you prefer not installing python, you can run the app via `docker-compose up`
    warning: there are complications with this.  See app notes.
    After the container is up, in another terminal run `docker-compose exec xml-to-turtle python3 xml_to_turtle.py --no_reset`
- docker-compose-production.yml
    a schema for running the app on Rancher 1.x
- Dockerfile

#### Non-git-commited files

- .env
    DM_API_USER=changeme
    DM_API_PASS=changeme
    DM_SAMBA_USER=changeme
    DM_SAMBA_PASS=changeme
    DM_PHOTO_FOLDER=changeme

- geckodriver, which you'll need to download and install (each OS does this differently)

### Bare-metal setup:

``sudo crontab -e`` contains the following lines:

```
# fetch data from digitalmeasures, write output to userfile.ttl, copy file to vivo, restart vivo
0 23 * * * python3 /usr/local/digitalmeasures-scripts/app/xml_to_turtle.py
0 0 * * * rsync -avz --chown=tomcat:tomcat /usr/local/digitalmeasures-scripts/output/turtles/userdata.ttl /usr/local/VIVO/home/rdf/abox/filegraph/userdata.ttl
0 0 * * * rsync -avz --chown=tomcat:tomcat /usr/local/digitalmeasures-scripts/output/person_images /usr/local/VIVO/home/uploads/filestorage_root/
10 0 * * * /bin/systemctl restart tomcat
```

### Rancher-based setup:

The userdata.ttl file is volume mounted onto the host filesystem.  The vivo container volume mounts that same file into its abox/filegraph/ path.  That path autoloads into Vivo on Vivo restart. 

```
docker build --no-cache --platform linux/x86_64/v8 -t libapps-admin.uncw.edu:8000/randall-dev/digitalmeasures-scripts/xml-to-turtle .
docker push libapps-admin.uncw.edu:8000/randall-dev/digitalmeasures-scripts/xml-to-turtle
```
