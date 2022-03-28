##### Physics (Obi)

# Solvers

Every Obi simulation requires at least one solver.

In TDW, the [`Obi` add-on](../../python/add_ons/obi.md) will automatically send [`create_obi_solver`](../../api/command_api.md#create_obi_solver.md) when it initializes or resets (see below). In most cases, this automatically-created solver will be sufficient for your simulation.

 You can send `create_obi_solver` more than once to create additional solvers.  There are two reasons to have more than one solver. First, Obi actors assigned to different solvers won't interact with each other. Second, each solver has a number of **substeps**. Substeps are sub-frames between `communicate()` calls. More substeps can increase the accuracy of the simulation at the cost of speed. Set the number of substeps per solver by sending [`set_obi_solver_substeps`](../../api/command_api.md#set_obi_solver_substeps).

Each solver has an integer ID corresponding to the order in which they were created:  The first solver is 0, the second is 1, and so on.

When resetting the scene for a new trial i.e. when `obi.reset()` is called, the `Obi` add-on sends [`destroy_obi_solver`](../../api/command_api.md#destroy_obi_solver) to destroy the initial solver (`solver_id` is 0). Send additional `destroy_obi_solver` commands to clean up any other solvers that you created.

***

**Next: [Robots and Obi](robots.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`Obi`](../../python/add_ons/obi.md)

Command API:

- [`create_obi_solver`](../../api/command_api.md#create_obi_solver.md)
- [`set_obi_solver_substeps`](../../api/command_api.md#set_obi_solver_substeps)
- [`destroy_obi_solver`](../../api/command_api.md#destroy_obi_solver)
