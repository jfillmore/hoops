#!/bin/sh



# Check if config file exists
if [ ! -f = "babel.cfg" ]
    then
    echo "[python: **.py]\n[jinja2: **/templates/**.html]\nextensions=jinja2.ext.autoescape,jinja2.ext.with_" > babel.cfg
fi

translations_directory='translations'

while getopts "eg:c:d:u:" opt; do
  case $opt in
    e)
      extract=true
      ;;
    g)
      generate=true
      language=$OPTARG
      ;;
    c)
      compile=true;
      ;;
    u)
      update=true
      ;;

    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ $extract ]
    then
    pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
fi

if [ $generate ]
    then
    pybabel init -i messages.pot -d $translations_directory -l $language
fi

if [ $compile ]
    then
    pybabel compile -d $translations_directory
fi

if [ $update ]
    then
    pybabel update -i messages.pot -d $translations_directory
fi
