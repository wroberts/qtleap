#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
create-EU-cond.py
(c) Will Roberts  24 June, 2016

Automates the creation of a new Basque experimental condition under
cuni_train.
'''

import errno
import os
import re
import sys
import click

def mkdir_p(path):
    '''
    Functionality similar to mkdir -p.
    '''
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

COND_NAME_REGEX = re.compile('(?P<lang>[a-z]{2,4})-(?P<corpus>[a-z]+)-(?P<cond>.+)')

CORPUS_NAME_DIR_MAPPING = {'eu':
                           {'elhuyar': 'train.token',
                            'indomain': 'elhuyar-indomain.e'},
}

CORPUS_NAME_PATH_MAPPING = {
    'eu':
    {'elhuyar': ('TRAIN_DATA=/work/robertsw/qtleap/elhuyar/train.token.baq; '
                 '/work/robertsw/qtleap/elhuyar/train.token.en'),
     'indomain': ('TRAIN_DATA=/work/robertsw/qtleap/elhuyar-indomain/elhuyar-indomain.eu; '
                  '/work/robertsw/qtleap/elhuyar-indomain/elhuyar-indomain.en')},
}

EXPT_DIR_NAME = {
    'eu': 'EU-expts',
}

SHORT_LANG_CODE_MAPPING = {
    'eu': 'eu',
}

LONG_LANG_CODE_MAPPING = {
    'eu': 'en_eu',
}

CORPUS_CONF_FILE_MAPPING = {
    'eu': 'conf/eu_en.conf',
}

THETA_CONF_FILE_MAPPING = {
    'eu': 'scenario/analysis/en_s4_analysis_a2t.scen',
}

def ensure_correct_corpus(conf_filename, lang, corpus):
    correct_cpline = CORPUS_NAME_PATH_MAPPING[lang][corpus]
    with open(conf_filename) as input_file:
        lines = input_file.read().strip().split('\n')
    cplines = [l for l in lines if l.startswith('TRAIN_DATA=')]
    if len(cplines) == 1 and cplines[0] == correct_cpline:
        return False
    # rewrite conf file
    with open(conf_filename, 'w') as output_file:
        # add correct line
        output_file.write(correct_cpline + '\n')
        # comment out incorrect lines
        for line in lines:
            if line.strip().startswith('TRAIN_DATA'):
                #output_file.write('#' + line.strip() + '\n')
                pass
            else:
                output_file.write(line + '\n')
    return True

def ensure_correct_theta(scen_filename, cond_theta):
    # either cond_theta is None, in which case there should be no MarkMWEs line
    # or it is a string (like 0.3), in which case the last line of the file should be
    # MarkMWEs phrase_list_path=/work/robertsw/qtleap/mwe-v2/MWE_ID_en.utf8.txt.gz comp_thresh=0.3
    correct_line = ('MarkMWEs '
                    'phrase_list_path=/work/robertsw/qtleap/mwe-v2/MWE_ID_en.utf8.txt.gz '
                    'comp_thresh={}').format(cond_theta)
    with open(scen_filename) as input_file:
        lines = input_file.read().strip().split('\n')
    last_line = [l.strip() for l in lines if l.strip()][-1]
    mwelines = [l.strip() for l in lines if l.strip().startswith('MarkMWEs')]
    if cond_theta is None and len(mwelines) == 0:
        return False
    if (cond_theta is not None
        and len(mwelines) == 1
        and mwelines[0] == correct_line
        and mwelines[0] == last_line):
        return False
    # rewrite file
    with open(scen_filename, 'w') as output_file:
        # comment out incorrect lines
        for line in lines:
            if line.strip().startswith('MarkMWEs'):
                #output_file.write('#' + line.strip() + '\n')
                pass
            else:
                output_file.write(line + '\n')
        # add correct line
        if cond_theta is not None:
            output_file.write(correct_line + '\n')
    return True

def symlink_points_to(link_path, target_path):
    return os.path.islink(link_path) and os.readlink(link_path) == target_path

@click.command()
@click.argument('cond_name')
def main(cond_name):
    '''
    Automates the creation of a new Basque experimental condition
    under cuni_train.

    Call with an argument something like eu-elhuyar-theta0.1
    '''
    print 'create new experimantal cond: {}'.format(cond_name)
    match = COND_NAME_REGEX.match(cond_name)
    if not match:
        print 'could not interpret condition name {}!'.format(cond_name)
        sys.exit(1)
    lang = match.group('lang')
    corpus = match.group('corpus')
    cond = match.group('cond')
    if lang not in CORPUS_NAME_DIR_MAPPING:
        print 'unrecognised language code {}!'.format(lang)
        sys.exit(1)
    if corpus not in CORPUS_NAME_DIR_MAPPING[lang]:
        print 'unrecognised corpus code {}!'.format(corpus)
        sys.exit(1)
    cond_theta = None
    if cond != 'baseline':
        try:
            assert cond.startswith('theta')
            cond_theta = cond[5:]
            _theta = float(cond_theta)
        except (AssertionError, ValueError):
            print 'Could not interpret condition code {}!'.format(cond)
            sys.exit(1)
    cond_dir = os.path.join(EXPT_DIR_NAME[lang], cond_name)
    tmp_dir = os.path.join(cond_dir, 'tmp')
    log_dir = os.path.join(cond_dir, 'log')
    if os.path.exists('tmp'):
        if not symlink_points_to('tmp', tmp_dir):
            print 'tmp already exists and points somewhere else!'
            sys.exit(1)
    if os.path.exists('log'):
        if not symlink_points_to('log', log_dir):
            print 'log already exists and points somewhere else!'
            sys.exit(1)
    #mkdir -p EU-expts/eu-elhuyar-theta0.1/{tmp,log}
    mkdir_p(tmp_dir)
    mkdir_p(log_dir)
    if os.listdir(log_dir):
        print '{} is not empty!'.format(log_dir)
        sys.exit(1)
    # ln -s EU-expts/${EXPTCOND}/{tmp,log} .
    # use relative paths in the symlinks
    os.symlink(tmp_dir, 'tmp')
    os.symlink(log_dir, 'log')
    # cd EU-expts/eu-elhuyar-theta0.1/tmp
    # mkdir -p eu_en/train.token/
    if os.path.exists(os.path.join(tmp_dir, LONG_LANG_CODE_MAPPING[lang])):
        print '{} already contains {}!'.format(tmp_dir, LONG_LANG_CODE_MAPPING[lang])
        sys.exit(1)
    para_data_dir = os.path.join(tmp_dir, LONG_LANG_CODE_MAPPING[lang],
                                 CORPUS_NAME_DIR_MAPPING[lang][corpus])
    mkdir_p(para_data_dir)
    # cd eu_en/train.token/
    # ln -s \
    # /work/robertsw/qtleap/qtleap/cuni_train/EU-expts/eu-elhuyar-baseline/tmp/eu_en/train.token/\
    # {data_splits,for_giza,giza_tmp,trees.morpho,trees.parse,concat_data.en,\
    # concat_data.eu,for_giza.gz,giza.gz,preproc_data.en,preproc_data.eu} .
    expts_abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 EXPT_DIR_NAME[lang])
    baseline_data_dir = os.path.join(expts_abspath,
                                     '{}-{}-baseline'.format(SHORT_LANG_CODE_MAPPING[lang], corpus),
                                     'tmp',
                                     LONG_LANG_CODE_MAPPING[lang],
                                     CORPUS_NAME_DIR_MAPPING[lang][corpus])
    if not os.path.exists(baseline_data_dir):
        print 'baseline model data dir {} not found!'.format(baseline_data_dir)
        sys.exit(1)
    for item in ['data_splits', 'for_giza', 'giza_tmp',
                 'trees.morpho', 'trees.parse',
                 'concat_data.en', 'concat_data.{}'.format(SHORT_LANG_CODE_MAPPING[lang]),
                 'for_giza.gz', 'giza.gz',
                 'preproc_data.en', 'preproc_data.{}'.format(SHORT_LANG_CODE_MAPPING[lang])]:
        source_path = os.path.join(baseline_data_dir, item)
        if not os.path.exists(source_path):
            print 'symlink source path {} not found!'.format(source_path)
            sys.exit(1)
        link_path = os.path.join(para_data_dir, item)
        os.symlink(source_path, link_path)
    # ensure that we have the right corpus selected
    edits_made = False
    edits_made = edits_made or ensure_correct_corpus(CORPUS_CONF_FILE_MAPPING[lang], lang, corpus)
    # now edit the relevant .scen file to set the theta value
    edits_made = edits_made or ensure_correct_theta(THETA_CONF_FILE_MAPPING[lang], cond_theta)
    if edits_made:
        print 'File(s) have been edited! Check git status.'
    print 'Success.'

if __name__ == '__main__':
    main()
