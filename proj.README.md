Make sure to ask Prosk nine questions.## About about 'proj' Project Manager.

Can you make a Linux command line application that's invoked with the command proj start and when run, loads an interactive menu in the terminal where the user is asked the following questions:

- enter the root directory of your project.
- Are there any other projects nested inside this project?Ifso, please list their locations.
- please list any programming languages that are used in this project.
- Does this project containa virtualenvironment,or is it runing in a container of anykind? If so, ple,
- Pase list its location.
- What is themostrecent version of the project?
- What is the location of the source folder for the project.
- Please list the locations of any test directories for the project.
- What is thelocation of the project's /.git/ folder?
- Pleaselist any locations in the project that should be ignored by the rest of the project.

...After asking the questions, it takes the provided data and stores it in the environment in the following variables:,

PROJ_ROOT: The route directory of the project.,
PROJ_SUBS: The locations of any subprojects contained within this project.,
PROJ_LANGS: A flattened array containing strings of any language used in the project,
PROJ_ENV: The project's environment, whether it be a virtual environment, a docker container or a regular file system,
PROJ_VSN: The project's current version,
PROJ_SRC: The location of the folder containing the source code for the project,
PROJ_TEST: The location of the project's test directory or directories,
PROJ_GITD: The location of the main git folder for the project.

- It also stores a .env file in the config directory of the .prj folder. The file will contain a list of the variables that it stored and their values, and will be in valid .ini format.
- Any answers for which the user gave multiple values will be stored in the form of a flattened Linux array with its separator as a colon, Or in other words, the value that you get by putting them in an array, then running: IFS=":"'; array[*]; It will just be a string that looks something like "value:value:value..." 
- After doing this, it will exit witha zero status and be done. 
- adequate error handling that is Linux compliant, with the ability to log its events at the proper log level with a logger. 
It will actually be two projects:
    - One project will be called when the calls the command on the command line, but this won't do anything 
        - unless the user invokes 'proj --help' or 'proj -h', in which case it will print out usage information and exit with a zero status 
        - this first program owns the 'proj' entry point, and is registered as the main command with Click, 
        - Click is the module that the app uses to create its command line interface. 
    - The second application will do all of the work and will register the 'start' subcommand as its entry pointso thatitowns thatscope 
    - in the future, there will be other sub-commands of the 'proj' command, and they need to work without having to refactor the projects that are already built. -

-The program writes a shell script, along with a .env file, and stores them both in the {project root}/.prj/config/ folder. the script uses the export command to add the variables and then immediately source the file. 
- It then adds a line to the rc file for the current user and for the shell that it was launched with that sources the script whenever it is run. 
- There is a config file to the config folder named 'conf' that has 3 options: 
        - "env-scope" which determines when the variables will exist in the environment (its values can be "when in project", "always", and "never"), 
        - "project-entry-hooks:" which is a list of scripts that will be run when the user enters the project,
        - "project-change-hooks:" which is a list of scripts that will be run when any of its files are changed. 
- There is a python module that owns the "proj conf" sub-command and 

    1. validates the config if the --validate or -v option is passed 
    2. reads the config and makes the changes needed. 

- It is the job of the main app (the one that owns the proj base command) to stay running and watch for project changes / make the needed actions 
- This project is. a complex network of modules working together to turn a project into a living breathing machine that makes its needed changes on its own.