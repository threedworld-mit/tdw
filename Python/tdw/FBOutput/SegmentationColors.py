# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FBOutput

import tdw.flatbuffers

class SegmentationColors(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsSegmentationColors(cls, buf, offset):
        n = tdw.flatbuffers.encode.Get(tdw.flatbuffers.packer.uoffset, buf, offset)
        x = SegmentationColors()
        x.Init(buf, n + offset)
        return x

    # SegmentationColors
    def Init(self, buf, pos):
        self._tab = tdw.flatbuffers.table.Table(buf, pos)

    # SegmentationColors
    def Ids(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # SegmentationColors
    def IdsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # SegmentationColors
    def IdsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # SegmentationColors
    def Names(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.String(a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return ""

    # SegmentationColors
    def NamesLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # SegmentationColors
    def Categories(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.String(a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return ""

    # SegmentationColors
    def CategoriesLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # SegmentationColors
    def Colors(self, j):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(tdw.flatbuffers.number_types.Int32Flags, a + tdw.flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # SegmentationColors
    def ColorsAsNumpy(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.GetVectorAsNumpy(tdw.flatbuffers.number_types.Int32Flags, o)
        return 0

    # SegmentationColors
    def ColorsLength(self):
        o = tdw.flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

def SegmentationColorsStart(builder): builder.StartObject(4)
def SegmentationColorsAddIds(builder, ids): builder.PrependUOffsetTRelativeSlot(0, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(ids), 0)
def SegmentationColorsStartIdsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SegmentationColorsAddNames(builder, names): builder.PrependUOffsetTRelativeSlot(1, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(names), 0)
def SegmentationColorsStartNamesVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SegmentationColorsAddCategories(builder, categories): builder.PrependUOffsetTRelativeSlot(2, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(categories), 0)
def SegmentationColorsStartCategoriesVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SegmentationColorsAddColors(builder, colors): builder.PrependUOffsetTRelativeSlot(3, tdw.flatbuffers.number_types.UOffsetTFlags.py_type(colors), 0)
def SegmentationColorsStartColorsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def SegmentationColorsEnd(builder): return builder.EndObject()
