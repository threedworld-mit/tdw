from tdw.backend.performance_benchmark_controller import PerformanceBenchmarkController

"""
Obi benchmark.
"""

c = PerformanceBenchmarkController(launch_build=False)

output = "| Without Obi | Without `ObiParticles` | With `ObiParticles` |" \
         "\n| --- | --- | --- |\n"
without_obi = c.run(boxes=True, obi=False, obi_particle_data=False)
without_particles = c.run(boxes=True, obi=True, obi_particle_data=False)
with_particles = c.run(boxes=True, obi=True, obi_particle_data=True)
output += f"| {without_obi} | {without_particles} | {with_particles} |"
c.communicate({"$type": "terminate"})
print(output)
