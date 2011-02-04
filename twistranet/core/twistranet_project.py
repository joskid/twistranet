from __future__ import with_statement
import os
import re
import sys
from optparse import OptionParser
import shutil
from uuid import uuid4, uuid1
import os

IGNORE_PATTERNS = ('.pyc','.git','.svn')

def twistranet_project():
    """
    Copies the contents of the project_template directory to a new directory
    specified as an argument to the command line.
    """
    # That is just to check that we can import the TN package.
    # If something goes wrong here, just add a --pythonpath option.     
    parser = OptionParser(
        usage = "usage: %prog [options] [<template>] <project_path>\n"
            "  where project_name is the name of the directory that will be created for your site,\n"
            "  <path> is the (optional) path where you want to install it.\n"
    )
    parser.add_option("-n", "--no-bootstrap",
        action="store_false", dest="bootstrap", default=True,
        help="Don't bootstrap project immediately. Use this if you want to review your settings before bootstraping.",
    )
    (options, args) = parser.parse_args()

    # Check template and path args
    if len(args) < 1:
        parser.error("project_path must be specified.")
    elif len(args) == 1:
        project_path = args[0]
        project_template = 'default'
    elif len(args) == 2:
        project_path = args[1]
        project_template = args[0]
    
    # Check if we can import TN.
    import twistranet
    
    # We decompose the given path to split installdir and project_name
    project_path = os.path.abspath(project_path)
    if os.path.lexists(project_path):
        parser.error("Directory '%s' already exists. "
            "Please specify a non-existing directory." % (project_path, ))
    project_name = os.path.split(project_path)[1]
    
    # Check if project_name is correct
    try:
        eval("%s is True" % project_name)
    except SyntaxError:
        parser.error("Directory '%s' must be a valid python identifier." % project_name)
    except:
        pass
    # Ensure the given directory name doesn't clash with an existing Python
    # package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    except ValueError:
        pass # It's ok to install in the same directory ;)
    else:
        parser.error("'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project name. "
            "Please try another name." % project_name)

    # Build the project up copying over the twistranet project_template
    twist_package = __import__('twistranet')
    twist_package_path = os.path.dirname(os.path.abspath(twist_package.__file__))
    template_dir = os.path.join(twist_package_path, "project_templates", "default")
    if not os.path.isdir(template_dir):
        parser.error("Template '%s' is invalid." % project_template)
    try:
        shutil.copytree(template_dir, project_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
    except AttributeError:
        print "shutil.copytree is likely not to have the 'ignore' attribute available.\n"
        shutil.copytree(template_dir, project_path)
    
    # If project_template <> default, we copy the project_template-specific files as well
    if project_template != "default":
        source_root = os.path.join(twist_package_path, "project_templates", project_template)
        dest_root = project_path
        for root, dirs, files in os.walk(source_root):
            relative_root = root[len(source_root) + 1:]
            for d in dirs:
                dest_dir = os.path.join(dest_root, relative_root, d)
                if not os.path.isdir(dest_dir):
                    os.mkdir(dest_dir)
            for fname in files:
                dest_file = os.path.join(dest_root, relative_root, fname)
                shutil.copy(
                    os.path.join(source_root, root, fname),
                    dest_file,
                )        
    
    # Generate variables replaced in the project files
    replacement = {
        "SECRET_KEY.*$":        "SECRET_KEY = '%s'" % (uuid1(), ),
    }
    
    # Write files, copy/replace things on-the-fly.
    settings_path = os.path.join(project_path, "local_settings.py")
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        for regex, repl in replacement.items():
            data = re.sub(regex, repl, data)
        f.write(data)
        
    # As we use a standard sqlite configuration, we can boostrap quite safely just now.
    # First we append project_path to sys.path, then we start the server.
    if options.bootstrap:
        from django.core.management import call_command
        from django import conf
        sys.path.insert(0, project_path)        # Here is how we're gonna find the 'settings' module from here.
        # XXX NOT VERY DJANGOISH TO USE JUST 'settings' HERE !
        os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
        os.environ["TWISTRANET_NOMAIL"] = "1"   # Disable emails
        import settings
        call_command('twistranet_bootstrap')
        
        # Now we can start the server!
        os.environ["TWISTRANET_NOMAIL"] = ""    # Re-enable emails
        call_command("runserver", "0.0.0.0:8000", use_reloader = False,  )

if __name__ == "__main__":
    twistranet_project()