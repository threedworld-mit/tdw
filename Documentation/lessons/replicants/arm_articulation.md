##### Replicants

# Arm articulation

Unlike [movement](movement.md) and [animations](animations.md), which are controlled by pre-recorded animation data, Replicant arm articulation is procedural. It uses inverse kinematic (IK) and the [FinalIK Unity asset](https://root-motion.com/) to solve an end pose, given a target position that a hand is reaching for.

## Reach for a target

The Replicant can reach for a target position or object via `reach_for(target, arm)`: