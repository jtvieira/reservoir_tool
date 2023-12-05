# reservoir_tool
This repo is for a reservoir level tool. Provides data analysis as well as predictive modeling of several California reservoirs.

## Requirements for running
Postgres must be installed on your machine
For installation instructions on mac, see here      : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-macos/
For installation instructions on windows, see here  : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/
For installation instructions on linux, see here    : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-linux/

The python packages for this project are listed in requirements.txt

There is a shell script called installPackages.sh
    Running this will create a new virtual environment and install all packages there

### Collecting Data

Run the collectData.sh script that is in the root directory of the project. This should create postgres databases with all of the information needed
