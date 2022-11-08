import os
from typing import OrderedDict
from psycopg2 import IntegrityError
from dateutil.tz import tzutc
import harvester.models as models
import datetime
import logging as logger
import sys
import imp
import inspect
import json
import ast

logger.basicConfig(level=logger.DEBUG)

def get_job_status_by_job_hash(cls, job_hashes, only_status = None):
    """
    Return all updates with job_hash
    """
    with cls.session_scope() as session:
        status = None
        logger.info("Opening Session")
        for job_hash in job_hashes:
            if only_status:
                record_db = session.query(models.gRPC_status).filter(models.gRPC_status.job_hash == job_hash).filter_by(status=only_status).first()
            else:
                record_db = session.query(models.gRPC_status).filter(models.gRPC_status.job_hash == job_hash).first()
            if record_db:
                status = record_db.status
                logger.info("{} has status: {}".format(record_db.job_hash, status))
            
    return status

def _get_job_by_job_hash(session, job_hash, only_status = None):
    """
    Return all updates with job_hash
    """
    status = None
    logger.info("Opening Session")

    if only_status:
        record_db = session.query(models.gRPC_status).filter(models.gRPC_status.job_hash == job_hash).filter_by(status=only_status).first()
    else:
        record_db = session.query(models.gRPC_status).filter(models.gRPC_status.job_hash == job_hash).first()
    if record_db:
        logger.info("Found record: {}".format(record_db.job_hash))
    return record_db

def write_job_status(cls, job_request, only_status = None):
    """
    Return all updates with job_hash
    """
    with cls.session_scope() as session:
        job_status = models.gRPC_status()
        job_status.job_hash = job_request.get("hash")
        job_status.job_request = job_request.get("task")
        job_status.status = job_request.get("status")
        job_status.timestamp = datetime.datetime.now()
        session.add(job_status)
        session.commit()
    return True

def update_job_status(cls, job_hash, status = None):
    """
    Return all updates with job_hash
    """
    updated = False
    with cls.session_scope() as session:
        job_status = _get_job_by_job_hash(session, job_hash)
        if job_status:
            job_status.status = status
            job_status.timestamp = datetime.datetime.now()
            session.add(job_status)
            session.commit()
            updated = True
    return updated


def load_config(proj_home=None, extra_frames=0, app_name=None):
    """
    Loads configuration from config.py and also from local_config.py
    :param: proj_home - str, location of the home - we'll always try
        to load config files from there. If the location is empty,
        we'll inspect the caller and derive the location of its parent
        folder.
    :param: extra_frames - int, number of frames to look back; default
        is 2, which is good when the load_config() is called directly,
        but when called from inside classes, we need to add extra more
    :return dictionary
    """
    conf = {}

    if proj_home is not None:
        proj_home = os.path.abspath(proj_home)
        if not os.path.exists(proj_home):
            raise Exception('{proj_home} doesnt exist'.format(proj_home=proj_home))
    else:
        proj_home = _get_proj_home(extra_frames=extra_frames)

    if proj_home not in sys.path:
        sys.path.append(proj_home)

    conf['PROJ_HOME'] = proj_home

    conf.update(load_module(os.path.join(proj_home, 'config.py')))
    conf.update(load_module(os.path.join(proj_home, 'local_config.py')))
    conf_update_from_env(app_name or conf.get('SERVICE', ''), conf)

    return conf

def _get_proj_home(extra_frames=0):
    """Get the location of the caller module; then go up max_levels until
    finding requirements.txt"""

    frame = inspect.stack()[2+extra_frames]
    module = inspect.getsourcefile(frame[0])
    if not module:
        raise Exception("Sorry, wasnt able to guess your location. Let devs know about this issue.")
    d = os.path.dirname(module)
    x = d
    max_level = 3
    while max_level:
        f = os.path.abspath(os.path.join(x, 'requirements.txt'))
        if os.path.exists(f):
            return x
        x = os.path.abspath(os.path.join(x, '..'))
        max_level -= 1
    sys.stderr.write("Sorry, cant find the proj home; returning the location of the caller: %s\n" % d)
    return d

def load_module(filename):
    """
    Loads module, first from config.py then from local_config.py
    :return dictionary
    """

    filename = os.path.join(filename)
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        pass
    res = {}
    from_object(d, res)
    return res

def conf_update_from_env(app_name, conf):
    app_name = app_name.replace(".", "_").upper()
    for key in list(conf.keys()):
        specific_app_key = "_".join((app_name, key))
        if specific_app_key in os.environ:
            # Highest priority: variables with app_name as prefix
            _replace_value(conf, key, os.environ[specific_app_key])
        elif key in os.environ:
            _replace_value(conf, key, os.environ[key])

def from_object(from_obj, to_obj):
    """Updates the values from the given object.  An object can be of one
    of the following two types:
    Objects are usually either modules or classes.
    Just the uppercase variables in that object are stored in the config.
    :param obj: an import name or object
    """
    for key in dir(from_obj):
        if key.isupper():
            to_obj[key] = getattr(from_obj, key)

def _replace_value(conf, key, new_value):
    try:
        w = json.loads(new_value)
        conf[key] = w
    except:
        try:
            # Interpret numbers, booleans, etc...
            conf[key] = ast.literal_eval(new_value)
        except:
            # String
            conf[key] = new_value