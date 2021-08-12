## Digital Measures to Turtle

#### Folders

- app/
    python code for creating a turtle file from DigitalMeasures (DM) repo
    Turtle file can be imported into Vivo
- experiments/
    jupyter notebooks for investigating the DM output
- output/
    non-git-committed folder holding output of app/xml_to_turtle.py

#### Non-git-commited files

- .env
    DMUSER=changeme
    DMPASS=changeme

#### Files that support all approaches

- requirements.txt
    `pip install -r requirement.txt` installs the python packages

##### Files that support the docker build (optional):

- crontab
    docker uses this to schedule what time to rerun the xml_to_turtle
- docker-compose.yml
    if you prefer not installing python, you can run the app via `docker-compose up`
    warning: there are complications with this.  See app notes.
- Dockerfile

