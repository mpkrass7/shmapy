# Lone Wolf
The fabulous (soon to be) package for building a United States hex map with optional hex filling.

## Install

Install from source: 
`git clone git@github.com:mpkrass7/lone_wolf.git`  
`python setup.py install` 

## Usage

```
pd.read_csv('static/demo_intput1.csv').head(20)
```

```bash
head -10 lone_wolf/static/demo_input1.csv
AK,0.448415868
AL,0.178259515
AR,0.094003348
AZ,0.263422391
CA,0.110670893
CO,0.179617281
CT,0.1960641
DC,0.171112619
DE,0.241586764
FL,0.040757232
```

`lone_wolf plot-hex static/demo_input1.csv`

![](./lone_wolf/img/hex_out.png)

`lone_wolf plot-hex static/demo_input1.csv -numeric_labels=all -size=8`

![](./lone_wolf/img/hex_out_label.png)

**Special Credits to Kevin Arvai and Gregory Michaelson because they are heroes**

## To Do Items:
- Users can fill hexagons with constant color rather than percent fill
- Users can supply custom cooridnates for the hexagons
- Users can fill hexagons on a gradient
- Users have **kwargs access to plot output to optionally include axes, title etc.. -- Some Kwargs are here!
- Improve filling mechanism to fill by area (Adrian halp please)
- Users can customize which states can be filled
- Users can supply values underneath state label -- DONE 