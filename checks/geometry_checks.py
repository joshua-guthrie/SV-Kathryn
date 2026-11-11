"""Reusable exact-solid classifiers for large shell acceptance checks."""
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
from OCP.gp import gp_Pnt


class Contains:
    def __init__(self,shape):
        self.bounds=shape.BoundingBox()
        self.classifiers=[BRepClass3d_SolidClassifier(s.wrapped) for s in shape.Solids()]

    def __call__(self,point):
        x,y,z=point
        bb=self.bounds
        if not (bb.xmin-1e-6<=x<=bb.xmax+1e-6 and bb.ymin-1e-6<=y<=bb.ymax+1e-6
                and bb.zmin-1e-6<=z<=bb.zmax+1e-6):
            return False
        for classifier in self.classifiers:
            classifier.Perform(gp_Pnt(x,y,z),1e-6)
            if classifier.State() in (TopAbs_IN,TopAbs_ON):
                return True
        return False
