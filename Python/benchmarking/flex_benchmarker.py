from tdw.controller import Controller
from tdw.add_ons.benchmark import Benchmark
from argparse import ArgumentParser
from platform import system
from benchmark_utils import PATH


"""
Benchmark a basic Flex simulation.
"""


class FlexBenchmarker(Controller):
    def run(self) -> float:
        self.communicate([{'$type': 'load_scene',
                           'scene_name': 'ProcGenScene'},
                          {'$type': 'create_exterior_walls',
                           'walls': [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 2}, {'x': 0, 'y': 3},
                                     {'x': 0, 'y': 4}, {'x': 1, 'y': 0}, {'x': 1, 'y': 4}, {'x': 2, 'y': 0},
                                     {'x': 2, 'y': 4}, {'x': 3, 'y': 0}, {'x': 3, 'y': 4}, {'x': 4, 'y': 0},
                                     {'x': 4, 'y': 1}, {'x': 4, 'y': 2}, {'x': 4, 'y': 3}, {'x': 4, 'y': 4}]},
                          {'$type': 'create_proc_gen_ceiling'},
                          {'$type': 'convexify_proc_gen_room'},
                          {'$type': 'create_avatar',
                           'id': 'a',
                           'type': 'A_Img_Caps_Kinematic'},
                          {'$type': 'teleport_avatar_to',
                           'position': {'x': -2, 'y': 1, 'z': -2}},
                          {'$type': 'set_avatar_forward',
                           'forward': {'x': 2, 'y': -1, 'z': 2}},
                          {'$type': 'send_avatars',
                           'frequency': 'always',
                           'ids': ['a']},
                          {'$type': 'send_camera_matrices',
                           'frequency': 'always',
                           'ids': ['a']},
                          {'$type': 'send_flex_particles',
                           'frequency': 'always'},
                          {'$type': 'set_pass_masks',
                           'pass_masks': ['_img']},
                          {'$type': 'create_flex_container',
                           'gravity': {'x': 0, 'y': -9.81, 'z': 0},
                           'radius': 0.1875,
                           'solid_rest': 0.125,
                           'fluid_rest': 0.115,
                           'static_friction': 0.5,
                           'dynamic_friction': 0.33333333,
                           'particle_friction': 0.166666666,
                           'substep_count': 8,
                           'iteration_count': 8,
                           'collision_distance': 0.0625,
                           'damping': 0.1,
                           'planes': [{'x': 0, 'y': 1, 'z': 0, 'w': 0}, {'x': 0, 'y': -1, 'z': 0, 'w': 5},
                                      {'x': 1, 'y': 0, 'z': 0, 'w': 2.2}, {'x': -1, 'y': 0, 'z': 0, 'w': 2.2},
                                      {'x': 0, 'y': 0, 'z': 1, 'w': 2.2}, {'x': 0, 'y': 0, 'z': -1, 'w': 2.2}]},
                          {'$type': 'set_time_step',
                           'time_step': 0.05},
                          {'$type': 'set_render_quality',
                           'render_quality': 0},
                          {'$type': 'set_post_process',
                           'value': False},
                          {'$type': 'load_primitive_from_resources',
                           'id': 1,
                           'primitive_type': 'Cube',
                           'position': {'x': 0.16403958415021425, 'y': 0.5186866147245053, 'z': 0.5172312486447144},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "scale_object",
                           "id": 1,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 1,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 1,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.21856892364500366},
                          {'$type': 'assign_flex_container',
                           'id': 1,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 1,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 1,
                           'color': {'r': 0.36824153984054797, 'g': 0.9571551589530464, 'b': 0.14035078041264515, 'a': 1}},
                          {'$type': 'load_primitive_from_resources',
                           'id': 2,
                           'primitive_type': 'Cube',
                           'position': {'x': 0.47383635425791626, 'y': 0.35827517721218594, 'z': -0.7295636531890959},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "scale_object",
                           "id": 2,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 2,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 2,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.22055267521432875},
                          {'$type': 'assign_flex_container',
                           'id': 2,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 2,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 2,
                           'color': {'r': 0.8700872583584364, 'g': 0.4736080452737105, 'b': 0.8009107519796442, 'a': 1}},
                          {'$type': 'load_primitive_from_resources',
                           'id': 3,
                           'primitive_type': 'Cube',
                           'position': {'x': -0.8337750147387952, 'y': 0.3888592806405162, 'z': -0.9812865902869348},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "scale_object",
                           "id": 3,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 3,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 3,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.5247127393571944},
                          {'$type': 'assign_flex_container',
                           'id': 3,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 3,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 3,
                           'color': {'r': 0.5204774795512048, 'g': 0.6788795301189603, 'b': 0.7206326547259168, 'a': 1}},
                          {'$type': 'send_collisions',
                           'frequency': 'always',
                           'enter': True,
                           'exit': False,
                           'stay': False},
                          {'$type': 'send_transforms',
                           'frequency': 'always'},
                          {'$type': 'teleport_and_rotate_flex_object',
                           'id': 1,
                           'position': {'x': 0.16403958415021425, 'y': 0.5186866147245053, 'z': 0.5172312486447144},
                           'rotation': {'x': -0.3698290892432926, 'y': 0.09343813858449268, 'z': -0.2922975854616724, 'w': 0.8769594520504459}},
                          {'$type': 'teleport_and_rotate_flex_object',
                           'id': 2,
                           'position': {'x': 0.47383635425791626, 'y': 0.35827517721218594, 'z': -0.7295636531890959},
                           'rotation': {'x': -0.26294416753798533, 'y': -0.28764056724783615, 'z': -0.32404784600690667, 'w': 0.862041914485243}},
                          {'$type': 'teleport_and_rotate_flex_object',
                           'id': 3,
                           'position': {'x': -0.8337750147387952, 'y': 0.3888592806405162, 'z': -0.9812865902869348},
                           'rotation': {'x': 0.2648241162596214, 'y': 0.23805685090753817, 'z': 0.263751099599952, 'w': 0.896455509572624}}])
        benchmark = Benchmark()
        benchmark.start()
        self.add_ons.append(benchmark)
        for i in range(2000):
            self.communicate([])
        benchmark.stop()
        return benchmark.fps


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--main', action='store_true')
    parser.add_argument('--machine', type=str, default='legion_lenovo', choices=['legion_lenovo', 'braintree', 'node11'])
    args = parser.parse_args()

    b = FlexBenchmarker(launch_build=False)
    fps = b.run()
    print(fps)

    if args.main:
        machine_key = args.machine.upper()
        if machine_key == "LEGION_LENOVO":
            if system() == "Windows":
                machine_key += "_WINDOWS"
            else:
                machine_key += "_UBUNTU"
        txt = PATH.read_text()
        txt = txt.replace("$FLEX_" + machine_key, str(int(fps)))
        PATH.write_text(txt)
    b.communicate({"$type": "terminate"})
