#/bin/bash

# wrote this script because the jupyter notebook 
# would the environment variables that are present in 
# bashrc

source $HOME/.bashrc

jupyter notebook \
--config=$HOME/.jupyter/jupyter_notebook_config.py \
--no-browser \
--notebook-dir=$HOME/agile/workspace