#!/bin/bash

# setup
tmux_session_bot=fs5Bot
tmux_session_web=fs5BotWeb
repository_url=https://github.com/Fachschaft5/fs5bot.git
declare -a required_packages=("python3" "pip3" "tmux" "git" "alembic")

# get applicatio dir and switch to it
application_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $application_dir

# check for test mode
if [ -f "testMode" ]
then
    test_mode=true
    echo "Info: Script is executed in test mode"
else
    test_mode=false
fi

# all functions
start() {
    echo "Start bot..."
	tmux new-session -d -s $tmux_session \; send-keys /"cd $app_dir ;python3 run.py" Enter
}
stop() {
    echo "Stop bot..."
	tmux kill-session -t $tmux_session
}
restart() {
    start
    stop
}

# check if on package is missing
for package in "${required_packages[@]}"; do
  if [ -z $(which $package) ]; then
    echo "Error: The package '$package' is missing."
    exit 1
  fi
done
echo "Info: All required packages were found."

# functions
function update_files {
    # start
    echo "Update files..."
    
    if [ $test_mode == true ]
    then
        echo "Info: Download is not executed (test mode activated)"
    else
	    cd $application_dir
        git clone $repository_url tmp
        cp -a tmp/* $application_dir
        chmod +x bot.sh
        rm -rf tmp
    fi

    # end
    echo "Success: Update completed"
}
function update_requirements {
    # start
    echo "Update requirements..."

    # install all requirements
	pip3 install -r requirements.txt

    # end
    echo "Success: Update completed"
}
function update_database {
    # start
    echo "Update database..."

    # update database
    alembic upgrade head

    # end
    echo "Success: Update completed"
}
function update_lanuages {
    # start
    echo "Update languages..."

    # cd to languages folder
    cd languages/

    # update all languages
    for language_dir in */
    do
        # check if base.po exist
        if [ -f ${language_dir%/}/LC_MESSAGES/base.po ]; then
            # generate .mo file
            echo "Update language '${language_dir%/}'..."
            msgfmt -o ${language_dir%/}/LC_MESSAGES/base.mo ${language_dir%/}/LC_MESSAGES/base
            echo "Success: Update language '${language_dir%/}'"
        fi
    done

    # end
    echo "Success: Update completed"
}
function update_all {
    update_files
    update_requirements
    update_database
    update_lanuages
}
function generate_languages {
    # start
    echo "Generate languages..."

    # get all textes in python files
    find . -iname "*.py" -not -path '*/venv/*'| xargs xgettext -d base -p languages -L Python

    # cd to languages folder 
    cd languages/

    # update all languages
    for language_dir in */
    do
        # check if base.po does not exist and create it if necessary
        if [ ! -f ${language_dir%/}/LC_MESSAGES/base.po ]; then
            echo "Create language file '${language_dir%/}'..."
            touch ${language_dir%/}/LC_MESSAGES/base.po
            echo "Success: Created language file '${language_dir%/}'"
        fi

        # merge langauge file
        echo "Generate language '${language_dir%/}'..."
        msgmerge --update ${language_dir%/}/LC_MESSAGES/base.po base.po
        echo "Success: Generate language '${language_dir%/}'"
    done
}
function test_mode {
    # check if config file exist
    if [ $test_mode == true ]
    then
        echo "Info: Test mode file was found"
    else
        echo "Info: Test mode file was not found"

        # create test mode file
        echo "Create test mode file..."
        touch testMode
        echo "Success: Creation completed"
    fi
}

# check command
case $1 in 
    "--install" )
        #webBackup_setup
        ;;
    "--update" )
        # check mode
        case $2 in
            "--files"|"-f" )
                update_files
                ;;
            "--requirements"|"-r" )
                update_requirements
                ;;
            "--database"|"-db" )
                update_database
                ;;
            "--lanuages"|"-l" )
                update_lanuages
                ;;
            "--all"|"-a" )
                update_all
                ;;
            *)
                echo "Error: Your input was incorrect, please have a look at the list of all commands here: https://github.com/Fachschaft5/fs5bot/wiki/Commands"
                exit 1
                ;;
        esac
        ;;
    "--dev" )
        # check mode
        case $2 in
            "--generate-languages"|"-gl" )
                generate_languages
                ;;
            "--testmode" )
                test_mode
                ;;
            *)
                echo "Error: Your input was incorrect, please have a look at the list of all commands here: https://github.com/Fachschaft5/fs5bot/wiki/Commands"
                exit 1
                ;;
        esac
        ;;
    "--test" )
        #does nothing
        ;;
    *)
        echo "Error: Your input was incorrect, please have a look at the list of all commands here: https://github.com/Fachschaft5/fs5bot/wiki/Commands"
        exit 1
        ;;
esac