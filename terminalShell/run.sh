#!/bin/bash

su -c "cd /home/limitado && ttyd -c $USER:$PASS --writable bash" limitado

# -c $USER:$PASS 

#su -c "ttyd -c $USER:$PASS  bash" limitado

