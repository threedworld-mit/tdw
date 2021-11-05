from tdw.backend.performance_benchmark_controller import PerformanceBenchmarkController

"""
Image capture benchmarks.
"""

output = "| 100 objects | Pass masks | Render quality | Post-processing | Screen size | .png | FPS |" \
         "\n| --- | --- | --- | --- | --- | --- | --- |\n"
c = PerformanceBenchmarkController(launch_build=False)
for boxes, pass_masks, render_quality, post_processing, screen_size, png in zip(
    [False, True, False, False, True, False, True, True],
    [["_img"], ["_id"], ["_img"], ["_img"], ["_id"], ["_img"], ["_img", "_id"], ["_img", "_id"]],
    [0, 0, 5, 5, 0, 5, 5, 5],
    [False, False, True, True, False, True, True, True],
    [256, 256, 256, 1024, 1024, 1024, 1024, 1024],
    [False, False, False, False, False, True, False, True]):
    fps = c.run(boxes=boxes, images=True, pass_masks=pass_masks, render_quality=render_quality,
                post_processing=post_processing, screen_size=screen_size, png=png, num_frames=2000)
    output += f"| {boxes} | `{pass_masks}` | {render_quality} | {post_processing} | {screen_size} | {png} | {fps} |\n"
c.communicate({"$type": "terminate"})
print(output)
