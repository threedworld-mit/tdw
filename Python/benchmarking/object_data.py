from tdw.backend.performance_benchmark_controller import PerformanceBenchmarkController

"""
Object data benchmarks.
"""

output = "| Transforms | Rigidbodies | Bounds | Collisions | FPS |" \
         "\n| --- | --- | --- | --- | --- |\n"
c = PerformanceBenchmarkController(launch_build=False)
for transforms, rigidbodies, bounds, collisions in zip(
        [True, False, False, False, True],
        [False, True, False, False, True],
        [False, False, True, False, True],
        [False, False, False, True, True]):
    fps = c.run(boxes=True, transforms=transforms, rigidbodies=rigidbodies, bounds=bounds, collisions=collisions,
                num_frames=2000)
    output += f"| {transforms} | {rigidbodies} | {bounds} | {collisions} | {fps} |\n"
c.communicate({"$type": "terminate"})
print(output)
