# Kathryn – Chesapeake Bay Skipjack

A 3D CAD model of the *Kathryn*, a historic Chesapeake Bay skipjack sailboat built in 1901.

The model was created using SOMA CAD and AI-assisted CAD modeling, using historic vessel drawings and archival photographs as references.

## Model files

- [Whole-boat STL](SV-Kathryn.stl)
- [SOMA project archive](SV-Kathryn.soma)
- [Source and reference package](src/) / [references/](references/)

## About Skipjacks

The Chesapeake Bay skipjack is a traditional wooden sailing vessel developed in the late 19th century to harvest oysters from the shallow waters of the Chesapeake Bay.

As the oyster industry expanded, watermen needed an affordable, efficient boat capable of working in shallow water. The skipjack answered that need with a relatively simple design: a broad, shallow-draft hull, a centerboard, and a single mast carrying a large mainsail and jib.

Typically ranging from 25 to 50 feet in length, skipjacks were designed specifically for oyster dredging. Their wide beam provided stability, while their shallow draft allowed them to reach oyster beds that larger vessels couldn't access.

They were working boats, not pleasure craft. Crews sailed across the oyster beds, dragging heavy metal dredges along the bottom to harvest oysters. Their design was practical, economical, and remarkably effective.

Although most closely associated with Maryland and the Chesapeake Bay, skipjacks and similar shallow-draft working sailing vessels were part of a broader maritime tradition extending south along the Atlantic coast. Related working sailing craft could be found as far south as Beaufort, North Carolina.

Today, the skipjack is an iconic symbol of Chesapeake Bay maritime history and Maryland's official state boat.

## Why the Kathryn?

I've always been fascinated by skipjacks.

They remind me of traditional sharpie sailboats, but they're considerably wider and have a much more substantial presence. Their proportions are unusual and appealing, combining the simplicity of a working sharpie with a broad hull that offers the potential for a proper cabin.

I've often thought that a skipjack would make a fascinating recreational sailboat, perhaps with a few modifications while retaining the character of the original design.

I would have loved to have built one.

Since that hasn't happened, creating a 3D model seemed like a good way to spend some time exploring the design.

## The Kathryn

The subject of this model is the *Kathryn*, a Chesapeake Bay skipjack built in 1901 in Crisfield, Maryland.

Some of her principal dimensions are:

| Specification    | Measurement         |
| ---------------- | ------------------- |
| Year Built       | 1901                |
| Length           | 50 feet             |
| Beam             | 16 feet 8 inches    |
| Depth            | 4 feet 2 inches     |
| Original Purpose | Oyster dredging     |
| Rig              | Single-masted sloop |

The *Kathryn* is particularly interesting because her hull differs from the more common hard-chine skipjack design. She features a V-bottom with a rounded chine and longitudinal planking, along with a distinctive convex bow and counter stern.

She is documented in the Historic American Engineering Record (HAER) and recognized as a National Historic Landmark.

## Creating the 3D Model

The model was created using **SOMA CAD**, an AI-assisted CAD application built around CadQuery.

This was a bit of an experiment in AI-assisted, or "vibe-coded," CAD modeling.

I supplied SOMA with the original historical drawings, photographs of the vessel, and some basic direction about what I wanted to create. The AI coding agent interpreted the reference material and generated the CAD geometry.

### SOMA CAD

[SOMA CAD](https://somacad.app/) is an open-source desktop application that allows you to create parametric 3D models using an AI coding agent.

Rather than manually constructing every component in a traditional CAD interface, you describe what you want to build, and the AI agent writes the underlying CAD code.

SOMA provides the environment to build, view, measure, and refine the resulting geometry.

- GitHub: [GitHub - Kai-Jungsthoefel/SOMA: Desktop app for designing parametric 3D models in CadQuery together with the coding agent of your choice · GitHub](https://github.com/Kai-Jungsthoefel/SOMA)

### CadQuery

SOMA uses [CadQuery](https://cadquery.readthedocs.io/), a Python-based parametric CAD framework.

CadQuery allows 3D geometry to be constructed programmatically using dimensions, profiles, extrusions, lofts, and other geometric operations.

The advantage is that the model is generated through editable code rather than being limited to a collection of manually created CAD features.

- GitHub: [GitHub - CadQuery/cadquery: A python parametric CAD scripting framework based on OCCT · GitHub](https://github.com/CadQuery/cadquery)

### The Result

For this project, I provided SOMA with the historical drawings and photographic references and let the AI agent do the heavy lifting.

The resulting CAD geometry was exported as an STL file.

The goal was to create a reasonably realistic three-dimensional representation of the *Kathryn*, capturing her distinctive hull proportions and overall appearance.

## Historical References

The model was based primarily on the following historical resources:

**National Park Service – National Historic Landmark Documentation**

Original historical documentation for the Kathryn:

https://npgallery.nps.gov/NRHP/GetAsset/NHLS/94001192_text

**Library of Congress – Historic American Engineering Record**

Archival photographs of the Kathryn:

https://www.loc.gov/resource/hhh.md1454.photos/?st=gallery&c=160

**Historic American Engineering Record – Kathryn**

Historic measured drawings and documentation:

https://www.loc.gov/pictures/item/md1454/

These drawings and photographs provided the reference material used to develop the 3D model.

## About the Model

This is a digital reconstruction based on the available historical drawings and photographs. Some details have necessarily been interpreted from the reference material.

The intention is to create a visually representative model of the original vessel, rather than a certified construction plan or exact reproduction.

The repository contains the CAD model and associated project files.

---

*The Kathryn is a reminder of a time when sail-powered working boats were an essential part of life along the Chesapeake Bay. It's a beautiful design, and one I would still love to build someday.*

**One small note:** I've retained the Beaufort reference in the broader context of Atlantic working-sailboat traditions rather than claiming that Chesapeake skipjacks themselves were routinely operated there.
