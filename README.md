# Bugsplainer Webapp

## Installation

Make sure you have `node`, `yarn` @ 1.x, `python` >= 3.7 and `CUDA` @ 1.13 installed in your machine/container.

Then, to install the node packages, run
```sh
yarn install
```

To install the python packages, run
```sh
pip install torch==1.11.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
pip install -r requirements.txt
```

## Run the application

```sh
yarn dev
```
