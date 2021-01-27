#!/usr/bin/env python

import argparse
import datetime
import glob
import os
import subprocess

import numpy as np
import tqdm

import matplotlib as mpl
import matplotlib.pyplot as plt


def git_get_branch():
    p = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True,
        )
    return p.stdout.decode().strip('\n"')


def git_checkout(ref):
    p = subprocess.run(
        ['git', 'checkout', ref],
        capture_output=True,
        )
    return p


def git_get_commits_hashes():
    p = subprocess.run(
        ['git', 'log', '--format="%H"'],
        capture_output=True,
        )
    return [h.strip('"') for h in p.stdout.decode().splitlines()]


def git_get_commit_timestamp():
    p = subprocess.run(
        ['git', 'show', '-s', '--format="%ct"'],
        capture_output=True,
        )
    return p.stdout.decode().strip('\n"')


def count_file_words(filename):
    p = subprocess.run(
        ['detex', '-n', '-w', filename],
        capture_output=True,
        )
    return len(p.stdout.splitlines())


def count_commit_words(files):
    filenames = glob.glob(files)
    count = sum([count_file_words(f) for f in filenames])
    return count


def get_commits_data(repo_dir, files):
    wdir = os.getcwd()

    try:
        os.chdir(repo_dir)
        branch = git_get_branch()

        try:
            commits_hashes = git_get_commits_hashes()
            commits_data = []
            for commit_hash in tqdm.tqdm(commits_hashes[::-1]):
                git_checkout(commit_hash)
                commit_timestamp = git_get_commit_timestamp()
                commit_word_count = count_commit_words(files)
                commits_data.append([
                    commit_timestamp,
                    commit_word_count,
                    ])

        finally:
            git_checkout(branch)

    finally:
        os.chdir(wdir)

    return commits_data


def save_commits_data(filename, data):
    with open(filename, 'w') as f:
        for line in data:
            line = [str(cell) for cell in line]
            line = ' '.join(line)
            line += '\n'
            f.write(line)


def load_commits_data(filename):
    with open(filename) as f:
        lines = f.read()
    commits_data = [
        [int(cell) for cell in line.split()]
        for line in lines.splitlines()
        ]
    return commits_data


def plot_commits_data(output_file, data, title=None):
    dates = [l[0] for l in data]
    word_count = [l[1] for l in data]
    dates = [datetime.datetime.fromtimestamp(int(d)) for d in dates]
    word_count = np.array(word_count)

    word_count_prefix = int(np.floor(np.log10(np.mean(word_count))))
    word_count = word_count / 10**word_count_prefix

    mpl.rcParams['axes.formatter.useoffset'] = False
    mpl.rcParams['xtick.minor.size'] = mpl.rcParams['xtick.major.size'] / 2.5

    fig = plt.figure(0, clear=True)
    ax = fig.gca()
    ax.plot(dates, word_count, '.-')
    if word_count_prefix != 0:
        ax.set_ylabel(f'Word count / $10^{word_count_prefix}$')
    else:
        ax.set_ylabel('Word count')
    ax.set_title(title)

    ax.xaxis.set_major_locator(mpl.dates.MonthLocator())
    ax.xaxis.set_minor_locator(mpl.dates.DayLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%Y-%m'))
    ax.format_xdata = mpl.dates.DateFormatter('%Y-%m-%d %H:%M')
    fig.autofmt_xdate()
    fig.tight_layout()

    ylim = plt.ylim()
    y_width = max(ylim) - min(ylim)
    plt.ylim(-0.05 * y_width, None)

    try:
        import etframes
        etframes.add_range_frame(ax, ybounds=[0, None])
    except ImportError:
        pass

    fig.savefig(output_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=('Count and plot the evolution of word number '
                     'in tex files in a git repo'))
    parser.add_argument(
        'repo_dir',
        type=str,
        help='Directory containing the git repo')
    parser.add_argument(
        'files',
        type=str,
        help='Path (or glob) to the files from which to count words')
    parser.add_argument(
        '--out-count',
        type=str,
        help=('File to which word counts are saved '
              '(default: {repo_dir}/wordcount.txt)'))
    parser.add_argument(
        '--out-plot',
        type=str,
        help=('File to which word counts plot is saved '
              '(default: {repo_dir}/wordcount_plot.pdf)'))
    parser.add_argument(
        '-t', '--plot-title',
        type=str,
        help=('plot title '
              '(default: {repo_dir}/{files})'))
    parser.add_argument(
        '--overwrite', '-O',
        action='store_true',
        help='Overwrite output files')
    parser.add_argument(
        '--plot-only',
        action='store_true',
        help='Only plot the data')
    args = parser.parse_args()

    if args.out_count is None:
        args.out_count = os.path.join(args.repo_dir, 'wordcount.txt')
    if args.out_plot is None:
        args.out_plot = os.path.join(args.repo_dir, 'wordcount_plot.pdf')
    if args.plot_title is None:
        args.plot_title = os.path.join(args.repo_dir, args.files)

    if not args.overwrite:
        if os.path.exists(args.out_count):
            msg = f'output file {args.out_count} exists (use -O to overwrite)'
            raise ValueError(msg)
        if os.path.exists(args.out_plot):
            msg = f'output file {args.out_plot} exists (use -O to overwrite)'
            raise ValueError(msg)

    if args.plot_only:
        commits_data = load_commits_data(args.out_count)
    else:
        commits_data = get_commits_data(args.repo_dir, args.files)
        save_commits_data(args.out_count, commits_data)
    plot_commits_data(args.out_plot, commits_data, title=args.plot_title)
