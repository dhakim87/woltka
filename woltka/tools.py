#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) 2020--, Qiyun Zhu.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Features under the `tools` command group.
"""

from sys import exit
from os import listdir
from os.path import isdir, join, basename
import click

from .table import (
    read_table, table_shape, filter_table, write_table, merge_tables)


def filter_wf(input_fp:      str,
              output_fp:     str,
              min_count:     int = None,
              min_percent: float = None):
    """Workflow for filtering a profile based on a per-sample threshold.

    Raises
    ------
    SystemExit
        Neither threshold is provided.
    SystemExit
        Both thresholds are provided.
    SystemExit
        Percentage threshold >= 100.

    See Also
    --------
    .cli.filter_cmd
        Command-line arguments and help information.
    """
    # validate parameters
    if not any((min_count, min_percent)):
        exit('Please specify either minimum count or minimum percentage '
             'threshold.')
    if all((min_count, min_percent)):
        exit('Only one of minimum count or minimum percentage thresholds '
             'can be specified.')
    if min_percent and min_percent >= 100:
        exit('Minimum percentage threshold must be below 100.')

    # determine threshold
    th = min_count or min_percent / 100

    # read input profile
    table, fmt = read_table(input_fp)
    n = table_shape(table)[0]
    click.echo(f'Number of features before filtering: {n}.')

    # filter profile by threshold
    click.echo('Filtered profile...', nl=False)
    table = filter_table(table, th)
    click.echo(' Done.')
    n = table_shape(table)[0]
    click.echo(f'Number of features after filtering: {n}.')

    # write filtered profile
    write_table(table, output_fp)
    click.echo('Filtered profile written.')


def merge_wf(input_fps: list,
             output_fp:  str):
    """Workflow for merging multiple profiles into one.

    Raises
    ------
    SystemExit
        Only one profile is provided.
    SystemExit
        Found invalid profile.

    See Also
    --------
    .cli.merge_cmd
        Command-line arguments and help information.
    """
    click.echo('Reading profiles...')
    tables = []

    def _read_profile(fp):
        try:
            table = read_table(fp)[0]
        except ValueError:
            exit(f'Cannot parse {basename(fp)} as a profile.')
        n, m = table_shape(table)
        click.echo(f'  Read {basename(fp)}. Samples: {m}, features: {n}.')
        tables.append(table)

    for fp in input_fps:
        if isdir(fp):
            for fname in listdir(fp):
                _read_profile(join(fp, fname))
        else:
            _read_profile(fp)

    if len(tables) == 1:
        exit('Please provide two or more profiles.')
    click.echo(f'Done. Number of profiles read: {len(tables)}.')

    # merge profiles
    click.echo('Merging profiles...', nl=False)
    table = merge_tables(tables)
    click.echo(' Done.')
    n, m = table_shape(table)
    click.echo(f'Number of samples after merging: {m}.')
    click.echo(f'Number of features after merging: {n}.')

    # write merged profile
    write_table(table, output_fp)
    click.echo('Merged profile written.')
