from tdw.backend.performance_benchmark_controller import PerformanceBenchmarkController

"""
Run the primary performance benchmarks.
"""

c = PerformanceBenchmarkController(launch_build=False)
fps = c.run(boxes=True, transforms=True, num_frames=20000)
print("Object data:", fps)
fps = c.run(images=True, pass_masks=["_img"], png=False, screen_size=256, post_processing=False, render_quality=0)
print("Image capture (low quality):", fps)
fps = c.run(images=True, pass_masks=["_img"], png=False, screen_size=1024, post_processing=True, render_quality=5)
print("Image capture (high quality):", fps)
fps = c.kitchen_benchmark()
print("Kitchen:", fps)
c.communicate({"$type": "terminate"})
