## Digital Measures to Turtle

Flags:
  - help 
  --no_reset  (prevents deletion of local dm folder.  dev timesaver)

#### Folders

- app/
    python code for creating a turtle file from DigitalMeasures (DM) repo
- experiments/
    jupyter notebooks for investigating the DM output
- output/
    non-git-committed folder holding output of app/xml_to_turtle.py
    you can import the userdata.ttl turtle file into Vivo

#### Files that support all approaches

- requirements.txt
    `pip install -r requirement.txt` installs the python packages

#### Files only used in the docker build (optional):

- crontab
    docker uses this to schedule what time to rerun the xml_to_turtle
- docker-compose.yml
    if you prefer not installing python, you can run the app via `docker-compose up`
    warning: there are complications with this.  See app notes.
- docker-compose-production.yml
    a schema for running the app on Rancher 1.x
- Dockerfile

#### Non-git-commited files

- .env
    DMUSER=changeme
    DMPASS=changeme

### Bare-metal setup:

``sudo crontab -e`` contains the following lines:

```
# fetch data from digitalmeasures, write output to userfile.ttl, copy file to vivo, restart vivo
0 23 * * * python3 /usr/local/digitalmeasures-scripts/app/xml_to_turtle.py
0 0 * * * rsync --chown=tomcat:tomcat /usr/local/digitalmeasures-scripts/output/turtles/userdata.ttl /usr/local/VIVO/home/rdf/abox/filegraph/userdata.ttl
10 0 * * * /bin/systemctl restart tomcat
```

### Rancher-based setup:

The userdata.ttl file is volume mounted onto the host filesystem.  The vivo container volume mounts that same file into its abox/filegraph/ path.  That path autoloads into Vivo on Vivo restart. 