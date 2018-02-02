## Notes for setting this up


#### The 'settings.py' file
Django needs to know where the custom "settings.py" module is.  Setting the environment variable will do it.
export DJANGO_SETTINGS_MODULE=conflusion.settings
If you are using Python Virtual Environments, this can be placed in the "[project_name]/bin/activate" file.  Just add it to the end of the file and that system will handle this for you.
