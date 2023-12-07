# reservoir_tool
This repo is for a reservoir level tool. Provides data analysis as well as predictive modeling of Lake Havasu and Lake Mohave.

## Requirements for running
Postgres must be installed and running on your machine
For installation instructions on mac, see here      : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-macos/
For installation instructions on windows, see here  : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/
For installation instructions on linux, see here    : https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql-linux/

The python packages for this project are listed in requirements.txt
This project also requires port 8000 to be free. Ensure that nothing is running on port 8000

### Collecting Data and Running project

There is a script called run.sh in the root directory of the project. It may be necessary to modify the permission of this file to turn it into an executable.
To do this, run chmod +x run.sh in the command line. 

#### Update DB Credentials in the .env file
For simplicity sake, I have included the .env file in this repository. While not a best practice, it is simpler this way. Enter your database credentials into here.

#### First run
If this is your first time running the project, you will need to ingest the data, install packages, train ML models, etc. 
run.sh will handle all of this if you include the -I flag. Run:
    ./run.sh -I

#### Subsequent runs
Because the majority of the required data is stored in a postgres database, every subsequent run of this project can be done by running:
    ./run.sh
You'll notice no flags. That is all that needs to be done

#### Cleaning up the project
As of now, cleaning the project will need to be done manually. The project creates a venv with all of the required packages. You will have to manually delete this directory (under the root of the project)
This project also creates 6 database tables. Those are:
    res_meta, res_data, havasu, mohave, mohave_results, havasu_results.
You can drop each of these tables manually.
