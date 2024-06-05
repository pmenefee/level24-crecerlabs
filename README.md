 # Voice App

## Overview
This project consists of two piplines, speech and voice recognition.


Be sure to change the value of __test_controller__ in src/settings.py to adjust which controller you will be using.


docker build -t level24-crecerlabs .
docker run --rm -it level24-crecerlabs-con -d -v $(pwd):/code level24-crecerlabs