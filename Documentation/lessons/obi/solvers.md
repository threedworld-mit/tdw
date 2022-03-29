##### Physics (Obi)

# Solvers

## Overview

Every Obi simulation requires at least one **solver**. In TDW, the [`Obi` add-on](../../python/add_ons/obi.md) will automatically send [`create_obi_solver`](../../api/command_api.md#create_obi_solver) when it initializes or resets (see below). In most cases, this automatically-created solver will be sufficient for your simulation.

Each solver has an integer ID corresponding to the order in which they were created:  The first solver is 0, the second is 1, and so on. 

Whenever you add actors such as [fluids](fluids.md), they must be assigned a solver. This is handled by a `solver_id` parameter; for example, `obi.create_fluid()` has an optional `solver_id` parameter (default value is 0).

##  Creating additional solvers

You can send `create_obi_solver` more than once to create additional solvers. There are two main reasons to do this:

1. Actors assigned to different solvers won't interact with each other.
2. Each solver has a number of **substeps**. Substeps are sub-frames between `communicate()` calls. More substeps can greatly increase the accuracy of the simulation at the cost of speed. Set the number of substeps per solver by sending [`set_obi_solver_substeps`](../../api/command_api.md#set_obi_solver_substeps).

## Destroying additional solvers

When resetting the scene for a new trial i.e. when `obi.reset()` is called, the `Obi` add-on sends [`destroy_obi_solver`](../../api/command_api.md#destroy_obi_solver) to destroy the initial solver. 

Send additional `destroy_obi_solver` commands to clean up any other solvers that you created.

***

**Next: [Robots and Obi](robots.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`Obi`](../../python/add_ons/obi.md)

Command API:

- [`create_obi_solver`](../../api/command_api.md#create_obi_solver)
- [`set_obi_solver_substeps`](../../api/command_api.md#set_obi_solver_substeps)
- [`destroy_obi_solver`](../../api/command_api.md#destroy_obi_solver)
