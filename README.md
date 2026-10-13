# SWMM Tools

**QGIS companion plugin for assigning SWMM subcatchment outlets without opening the attribute table.**

SWMM Tools stores which layers are your subcatchments, junctions and outfalls, then lets you click a subcatchment and a node to write the node's `Name` into the subcatchment `Outlet` field. It is meant to sit beside **Generate SWMM Inp**. It does not write an EPA SWMM `.inp` file.

![QGIS](https://img.shields.io/badge/QGIS-3.16%2B-green)
![Version](https://img.shields.io/badge/version-v1.1-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-orange)

## Main features

- Configure Layers: pick subcatchment, junction, outfall, and longest flowpath layers
- Layer and field choices saved in the QGIS project
- Configurable outlet field and node ID fields (defaults: `Outlet` and `Name`)
- Assign Outlet map tool: click a subcatchment, then a node
- Writes the node ID into the subcatchment outlet field
- Calculate Width: clips longest-flowpath lines to each subcatchment and writes `Width = Area / Longest Flowpath`
- Highlight of the selected subcatchment while you pick a node
- Esc or right-click cancels the current subcatchment

## Typical workflow

1. Load your SWMM polygon, point, and line layers in QGIS.
2. Open **Configure Layers** and select the layers (and optionally the outlet/ID fields).
3. Turn on **Assign Outlet**.
4. Click a subcatchment, then click a junction or outfall.
5. Run **Calculate Width** if you have a longest flowpath layer.
6. Generate the `.inp` with the Generate SWMM Inp plugin when ready.

## Installation from ZIP (outside of QGIS Plugin Repository)

1. Zip this whole github repo. 
2. Open QGIS.
3. Go to **Plugins → Manage and Install Plugins → Install from ZIP**.
4. Select the zip file.
5. Enable **SWMM Tools**.

## Requirements

- QGIS 3.16 or later (developed on QGIS 3.44 LTR)
- Polygon subcatchments
- Point junctions and/or outfalls
- Optional line layer for longest flowpath
- Default field names: `Outlet`, `Name`, `Width` (configurable for outlet and ID fields)

## Demo Video


https://github.com/user-attachments/assets/b1e193fb-f9b2-48a6-8a1c-6b36ae08a3c8



## Repository structure

```text
SWMM-Tools/
├── __init__.py
├── swmmtools.py
├── config.py
├── config_dialog.py
├── assign_outlet.py
├── helper_functions/
│   ├── __init__.py
│   └── calculate_width.py
├── icon.png
├── metadata.txt
├── README.md
├── LICENSE
└── .gitignore

