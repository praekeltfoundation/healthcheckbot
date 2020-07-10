# healthcheckbot

## Running locally
```bash
~ export BOT=base
~ export LANG=en
~ pip install -r requirements.txt -r requirements-dev.txt -r requirements-actions.txt
~ ./shell.sh $BOT $LANG
```

### Running linting and tests
```bash
~ ./test.sh $BOT $LANG
```

## Bots
This repo has a folder for each bot.
Inside each bot folder, there is a separate domain file for each language

### base
This is the main, public HealthCheck. Other healthcheck bots are based upon this one.
It has the following languages:

`eng`: English


### dbe
This is the HealthCheck for the Department of Basic Education / E3. 
It has an import of the actions, a copy of the domain, and a symlink for all the data
files.
It has the following languages:

`eng`: English
