#!/bin/bash

PYTHON=python3.6
SRC=.

# cd ./Virtual-Route

tmux new-session -s test-controller -n controller -d
tmux split-window -h -p 50 -t "test-controller":0.0
tmux split-window -v -p 50 -t "test-controller":0.0
tmux split-window -v -p 50 -t "test-controller":0.1

tmux send -t "test-controller":0.0 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.1 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.2 "$PYTHON $SRC/controller_client.py" Enter
tmux send -t "test-controller":0.3 "$PYTHON $SRC/controller.py" Enter

tmux send -t "test-controller":0.1 '1' Enter
tmux send -t "test-controller":0.1 'n' Enter
tmux send -t "test-controller":0.2 '2' Enter
tmux send -t "test-controller":0.2 'n' Enter
tmux send -t "test-controller":0.0 '0' Enter
tmux send -t "test-controller":0.0 'y' Enter
tmux send -t "test-controller":0.0 'Hello, World!' Enter
tmux send -t "test-controller":0.0 '127.0.0.1' Enter
tmux send -t "test-controller":0.0 '9002' 

tmux choose-window -t "test-controller":0.0

# cd ..

tmux a -t test-controller
