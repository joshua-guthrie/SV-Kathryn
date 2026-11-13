"""Exact material partitioning: separate board solids without retained backing."""
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Splitter
from OCP.TopTools import TopTools_ListOfShape
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections


def split_material(shape,tools,parallel=False):
    arguments=TopTools_ListOfShape();arguments.Append(shape.wrapped)
    cutting=TopTools_ListOfShape()
    for tool in tools:cutting.Append(tool.wrapped)
    operation=BRepAlgoAPI_Splitter()
    operation.SetArguments(arguments)
    operation.SetTools(cutting)
    operation.SetNonDestructive(True)
    operation.SetRunParallel(parallel)
    operation.SetFuzzyValue(1e-7)
    operation.Build()
    assert operation.IsDone(),'Board partition failed'
    result=cq.Shape.cast(operation.Shape())
    pieces=[s for s in result.Solids() if s.Volume()>1e-8]
    assert all(s.isValid() for s in pieces),'Invalid board partition'
    # Default GProp integration is too loose for long spline faces; use the
    # same explicit high-accuracy integration on source and partition pieces.
    total=sum(s.Volume(1e-9) for s in pieces);reference=shape.Volume(1e-9)
    # One part per million accommodates accumulated fuzzy-intersection/GProp
    # roundoff on the spline shell (observed 0.12 ppm), while rejecting actual
    # missing regions such as the earlier open-surface cutter failure.
    assert abs(total-reference)<max(1e-6,reference*1e-6),('Board material partition discrepancy',total,reference,total-reference)
    return pieces


def plane_x(x):
    return cq.Face.makeFromWires(cq.Workplane('YZ',origin=(x,0,0)).rect(160,60).val())


def plane_f(f):
    return cq.Face.makeFromWires(cq.Workplane('XZ',origin=(0,25-f,0)).rect(50,60).val())


def plane_z(z):
    return cq.Face.makeFromWires(cq.Workplane('XY',origin=(0,0,z)).rect(50,160).val())


def seam_surface(segments):
    loft=BRepOffsetAPI_ThruSections(False,False,1e-6)
    loft.CheckCompatibility(False)
    loft.SetMaxDegree(3)
    for a,b in segments:
        loft.AddWire(cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*b))]).wrapped)
    loft.Build()
    assert loft.IsDone(),'Could not construct board seam surface'
    return cq.Shape.cast(loft.Shape())


def smooth_loft(wires):
    """Dense source sections, cubic longitudinal interpolation, fixed topology."""
    loft=BRepOffsetAPI_ThruSections(True,False,1e-7)
    loft.CheckCompatibility(False)
    loft.SetMaxDegree(3)
    for wire in wires:loft.AddWire(wire.wrapped)
    loft.Build()
    assert loft.IsDone(),'Source-section cubic loft failed'
    result=cq.Shape.cast(loft.Shape())
    assert result.isValid() and len(result.Solids())==1,'Invalid source-section cubic loft'
    return result


def segmented_loft(wires,intervals=12):
    """Bound spline complexity so later plank/slot booleans stay tractable."""
    pieces=[]
    for start in range(0,len(wires)-1,intervals):
        pieces.append(smooth_loft(wires[start:min(len(wires),start+intervals+1)]))
    shape=pieces[0].fuse(*pieces[1:]).clean() if len(pieces)>1 else pieces[0]
    assert shape.isValid() and len(shape.Solids())==1,'Invalid segmented source loft'
    return shape


def ruled_loft(wires):
    loft=BRepOffsetAPI_ThruSections(True,True,1e-7)
    loft.CheckCompatibility(False)
    for wire in wires:loft.AddWire(wire.wrapped)
    loft.Build()
    assert loft.IsDone(),'Ruled tool loft failed'
    shape=cq.Shape.cast(loft.Shape())
    assert shape.isValid() and len(shape.Solids())==1,'Invalid ruled tool loft'
    return shape
