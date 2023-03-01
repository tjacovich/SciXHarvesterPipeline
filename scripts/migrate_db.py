from alembic.script import ScriptDirectory
from alembic.config import Config
from io import StringIO
from alembic.command import history, current, upgrade, downgrade
from collections import OrderedDict
import os
import subprocess

# purpose of this script is to discover what version of a db schema
# is deployed and what *should* be deployed; and decide whether we
# need to upgrade or downgrade. It does so by inspecting db schema
# and the versions saved in the alembic directory. So this script is
# to be run *from inside the desired release*

def load_revisions(config):
    # harvest revision graph from the filesystem (oldest last)
    revisions = []
    script = ScriptDirectory.from_config(config)
    for x in script.walk_revisions('base', 'heads'):
        revisions.append(x)

    # more natural order (oldest first)
    revisions = list(reversed(revisions))
    
    out = OrderedDict()
    for x in revisions:
        out[x.revision] = x
    
    return out

def get_current(config):
    stdout = config.stdout
    config.stdout = StringIO()
    try:
        current(config)
        config.stdout.seek(0)
        x = config.stdout.read()
        head_db = x.strip().split('\n')[-1].split(' ')[0]
    except Exception as e:
        if 'locate revision' in str(e):
            head_db = str(e).strip().split(' ')[-1].replace("'", '')
        else:
            raise
    return head_db

def run(alembic_config=os.environ.get('ALEMBIC_CONFIG_LOCATION', '/app/alembic.ini')):

    config = Config(alembic_config)
    script = ScriptDirectory.from_config(config)

    # latest version on filesystem
    head_fs = script.get_current_head()

    revisions = load_revisions(config)

    # retrieve the current db version
    head_db = get_current(config)

    

    print ('Comparing database states; desired version = %s; running version = %s' % (head_fs, head_db))

    if head_db and head_fs and head_db == head_fs:
        print('Db schema is on revision (%s) which is also the latest head for alembic revisions; no need to do anything' % (head_db,))
    else:
        print('Db schema is on revision %s while desired revision is: %s' % (head_db, head_fs))

        existing = None
        desired = None
        repo_version = None

        if head_fs in revisions:
            desired = revisions[head_fs]
        if head_db in revisions:
            existing = revisions[head_db]

        if desired is None: # can only happen if something pulls carpet from under our feet...
            raise Exception('The desired revision is NOT found inside alembic/revisions')
        if existing is None:
            print('Db is running a version which is not described by alembic/revisions. We must fetch those revisions first')

            repo_version = subprocess.check_output('git describe', shell=True)
            print('Your repo is running version: %s' % repo_version)

            print('We dont know which commit contains the proper (future) revisions, so we are going to get ALEMBIC_RELEASE or latest HEAD of alembic/versions')
            target_commit = os.environ.get('ALEMBIC_RELEASE', 'HEAD')
            print('Going to get: %s' % (target_commit, ))

            subprocess.check_call('git fetch', shell=True)
            subprocess.check_call('rm -fr alembic/versions.old; mv -f alembic/versions alembic/versions.old', shell=True)
            print(subprocess.check_output('git checkout %s -- alembic/versions' % (target_commit,), shell=True))

            revisions = load_revisions(config)
            if head_db in revisions:
                existing = revisions[head_db]
            
            if existing is None:
                print('Refusing to continue. Was not able to retrieve alembic/revisions which describe %s.' % (head_db,))
                subprocess.check_call('rm -fr alembic/versions')
                subprocess.check_call('mv alembic/versions.old alembic/versions')
                raise Exception('Db is running some version (%s) that is NOT desribed by alembic' % (head_db,))


        idx = list(revisions.keys()).index(desired.revision)
        idx_existing = list(revisions.keys()).index(existing.revision)

        config = Config(alembic_config) # reset stdout

        if idx >= idx_existing:
            print('We are going to upgrade db schema %s versions forward', (idx_existing - idx,))
            upgrade(config, desired.revision)
        else:
            print('We are going to downgrade db schema %s versions back', (idx - idx_existing,))
            downgrade(config, desired.revision)

        if repo_version:
            subprocess.check_call('rm -fr alembic/versions*', shell=True)
            subprocess.check_call('git checkout -- alembic/versions', shell=True)


if __name__ == '__main__':
    if os.environ.get('ALEMBIC_RUN_MIGRATION', 'True').lower().strip() == 'true':
        run()
    else:
        print('ALEMBIC_RUN_MIGRATION is not set; we are not going to run schema migration')