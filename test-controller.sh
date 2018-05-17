#!/bin/bash

PYTHON=python3.6
SRC=.

# cd ./Virtual-Route

tmux new-session -s test-controller -n controller -d
tmux split-window -h -p 66 -t "test-controller":0.0
tmux split-window -h -p 50 -t "test-controller":0.1
tmux split-window -v -p 50 -t "test-controller":0.0
tmux split-window -v -p 50 -t "test-controller":0.1
tmux split-window -v -p 50 -t "test-controller":0.2

tmux send -t "test-controller":0.0 "$PYTHON $SRC/controller.py" Enter
tmux send -t "test-controller":0.1 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.2 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.3 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.4 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.5 "$PYTHON $SRC/controller_client.py" Enter

tmux send -t "test-controller":0.1 '1' Enter
tmux send -t "test-controller":0.1 'n' Enter
tmux send -t "test-controller":0.2 '2' Enter
tmux send -t "test-controller":0.2 'n' Enter
tmux send -t "test-controller":0.3 '4' Enter
tmux send -t "test-controller":0.3 'n' Enter
tmux send -t "test-controller":0.4 '5' Enter
tmux send -t "test-controller":0.4 'n' Enter

tmux send -t "test-controller":0.5 '0' Enter
tmux send -t "test-controller":0.5 'y' Enter
tmux send -t "test-controller":0.5 'Hello, World!' Enter
tmux send -t "test-controller":0.5 '127.0.0.1' Enter
tmux send -t "test-controller":0.5 '9005'

# tmux choose-window -t "test-controller":0.0

# cd ..

tmux a -t test-controller
