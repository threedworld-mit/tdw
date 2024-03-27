# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class Fove(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsFove(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = Fove()
        x.Init(buf, n + offset)
        return x

    # Fove
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # Fove
    def EyeDirections(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # Fove
    def EyeDirectionsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Float32Flags, o)
        return 0

    # Fove
    def EyeDirectionsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Fove
    def EyeStates(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Uint8Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # Fove
    def EyeStatesAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Uint8Flags, o)
        return 0

    # Fove
    def EyeStatesLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Fove
    def ObjectHits(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.BoolFlags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # Fove
    def ObjectHitsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.BoolFlags, o)
        return 0

    # Fove
    def ObjectHitsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Fove
    def ObjectIds(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # Fove
    def ObjectIdsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # Fove
    def ObjectIdsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Fove
    def CombinedDepth(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(tdw.flatbuffers.number_types.Float32Flags, o + self._tab.Pos)
        return 0.0

def FoveStart(builder): builder.StartObject(5)
def FoveAddEyeDirections(builder, eyeDirections): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(eyeDirections), 0)
def FoveStartEyeDirectionsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def FoveAddEyeStates(builder, eyeStates): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(eyeStates), 0)
def FoveStartEyeStatesVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def FoveAddObjectHits(builder, objectHits): builder.PrependUOffsetTRelativeSlot(2, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(objectHits), 0)
def FoveStartObjectHitsVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def FoveAddObjectIds(builder, objectIds): builder.PrependUOffsetTRelativeSlot(3, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(objectIds), 0)
def FoveStartObjectIdsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def FoveAddCombinedDepth(builder, combinedDepth): builder.PrependFloat32Slot(4, combinedDepth, 0.0)
def FoveEnd(builder): return builder.EndObject()
