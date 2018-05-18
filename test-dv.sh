#!/bin/bash

PYTHON=python3.6
SRC=.

tmux new-session -s test-dvroute -n dvroute -d
tmux split-window -h -p 66 -t "test-dvroute":0.0
tmux split-window -h -p 50 -t "test-dvroute":0.1
tmux split-window -v -p 50 -t "test-dvroute":0.0
tmux split-window -v -p 50 -t "test-dvroute":0.1
tmux split-window -v -p 50 -t "test-dvroute":0.2

tmux send -t "test-dvroute":0.0 "$PYTHON $SRC/dv_router.py" Enter
tmux send -t "test-dvroute":0.1 "$PYTHON $SRC/dv_router.py" Enter
tmux send -t "test-dvroute":0.2 "$PYTHON $SRC/dv_router.py" Enter
tmux send -t "test-dvroute":0.3 "$PYTHON $SRC/dv_router.py" Enter
tmux send -t "test-dvroute":0.4 "$PYTHON $SRC/dv_router.py" Enter
tmux send -t "test-dvroute":0.5 "$PYTHON $SRC/dv_router.py" Enter

tmux send -t "test-dvroute":0.0 '1' Enter
tmux send -t "test-dvroute":0.0 'n' Enter
tmux send -t "test-dvroute":0.1 '2' Enter
tmux send -t "test-dvroute":0.1 'n' Enter
tmux send -t "test-dvroute":0.2 '3' Enter
tmux send -t "test-dvroute":0.2 'n' Enter
tmux send -t "test-dvroute":0.3 '4' Enter
tmux send -t "test-dvroute":0.3 'n' Enter
tmux send -t "test-dvroute":0.4 '5' Enter
tmux send -t "test-dvroute":0.4 'y' Enter

tmux send -t "test-dvroute":0.5 '0' Enter
tmux send -t "test-dvroute":0.5 'y' Enter
tmux send -t "test-dvroute":0.5 'Hello, World!' Enter
# tmux send -t "test-dvroute":0.5 'exit' Enter
tmux send -t "test-dvroute":0.5 '5' Enter

tmux a -t test-dvroute
