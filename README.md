# Count and plot the evolution of word number in tex files in a git repo


## Usage

~~~
usage: wordcount_tex_git.py [-h] [--out-count OUT_COUNT] [--out-plot OUT_PLOT] [-t PLOT_TITLE] [--overwrite] [--plot-only]
                            repo_dir files

Count and plot the evolution of word number in tex files in a git repo

positional arguments:
  repo_dir              Directory containing the git repo
  files                 Path (or glob) to the files from which to count words

optional arguments:
  -h, --help            show this help message and exit
  --out-count OUT_COUNT
                        File to which word counts are saved (default: {repo_dir}/wordcount.txt)
  --out-plot OUT_PLOT   File to which word counts plot is saved (default: {repo_dir}/wordcount_plot.pdf)
  -t PLOT_TITLE, --plot-title PLOT_TITLE
                        plot title (default: {repo_dir}/{files})
  --overwrite, -O       Overwrite output files
  --plot-only           Only plot the data
~~~

## License

This package is released under a MIT open source licence. See `LICENSE.txt`.
