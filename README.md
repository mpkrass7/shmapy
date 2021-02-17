# Lone Wolf
The fabulous (soon to be) package for building a United States hex map with optional hex filling.

## Install

Install from source: 
`git clone git@github.com:mpkrass7/lone_wolf.git`  
`python setup.py install` 

## Usage

`lone-wolf plot-hex static/demo_input1.csv`

![](hex_out.png)

**Special Credits to Kevin Arvai and Gregory Michaelson because they are heroes**

## To Do Items:
- Users can fill hexagons with constant color rather than percent fill
- Users can supply custom cooridnates for the hexagons
- Users can fill hexagons on a gradient
- Users have **kwargs access to plot output to optionally include axes, title etc..
- Improve filling mechanism to fill by area (Adrian halp please)