from tdw.backend.performance_benchmark_controller import PerformanceBenchmarkController

"""
Observation data benchmarks.
"""

output = "| _img pass | _id pass | IdPassSegmentationColors | Occlusion | FPS |" \
         "\n| --- | --- | --- | --- | --- |\n"
c = PerformanceBenchmarkController(launch_build=False)
for images, pass_masks, id_colors, occlusion in zip(
        [True, True, False, False],
        [["_img"], ["_id"], None, None],
        [False, False, True, False],
        [False, False, False, True]):
    fps = c.run(boxes=True, images=images, pass_masks=pass_masks, id_colors=id_colors, occlusion=occlusion,
                num_frames=2000)
    img_pass = True if pass_masks is not None and "_img" in pass_masks else False
    id_pass = True if pass_masks is not None and "_id" in pass_masks else False
    output += f"| {img_pass} | {id_pass} | {id_colors} | {occlusion} | {fps} |\n"
c.communicate({"$type": "terminate"})
print(output)
