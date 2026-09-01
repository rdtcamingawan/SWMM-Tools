# SWMM Tools

**QGIS companion plugin for assigning SWMM subcatchment outlets without opening the attribute table.**

SWMM Tools stores which layers are your subcatchments, junctions and outfalls, then lets you click a subcatchment and a node to write the node's `Name` into the subcatchment `Outlet` field. It is meant to sit beside **Generate SWMM Inp**. It does not write an EPA SWMM `.inp` file.

![QGIS](https://img.shields.io/badge/QGIS-3.16%2B-green)
![Version](https://img.shields.io/badge/version-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-orange)

## Main features

- Configure Layers: pick the subcatchment, junction and outfall layers once
- Layer choice saved in the QGIS project (layer id, then layer name)
- Assign Outlet map tool: click a subcatchment, then a node
- Writes `Name` from the node into `Outlet` on the subcatchment
- Works with junction and outfall point layers
- Highlight of the selected subcatchment while you pick a node
- Esc or right-click cancels the current subcatchment

## Typical workflow

1. Load your SWMM polygon and point layers in QGIS.
2. Confirm subcatchments have a text field `Outlet`.
3. Confirm junctions and outfalls have a field `Name`.
4. Open **Configure Layers** and select the three layers.
5. Turn on **Assign Outlet**.
6. Click a subcatchment, then click a junction or outfall.
7. Continue around the model. Generate the `.inp` with the Generate SWMM inp plugin when all layers are set.

## Installation from ZIP (outside of QGIS Plugin Repository)

1. Zip this whole github repo. 
2. Open QGIS.
3. Go to **Plugins → Manage and Install Plugins → Install from ZIP**.
4. Select the zip file.
5. Enable **SWMM Tools**.

## Requirements

- QGIS 3.16 or later (developed on QGIS 3.44 LTR)
- Polygon subcatchments with field `Outlet`
- Point junctions and point outfalls with field `Name`

Those field names are fixed in this version. Use a projected CRS. Node snap is 50 map units.

## Repository structure

```text
SWMM-Tools/
├── __init__.py
├── swmmtools.py
├── config.py
├── config_dialog.py
├── assign_outlet.py
├── icon.png
├── metadata.txt
├── README.md
├── LICENSE
└── .gitignore