##### Core Concepts

# Design philosophy of TDW

## 1. Low-level atomic API

The API is designed to be as low-level as possible. Each API call (a "command" in TDW) is typically designed to do exactly one thing. It is possible to send multiple commands at once to achieve complex behavior. Likewise, TDW doesn't return [output data](output_data.md) by default; it must be explicitly requested.

There are several key advantages to this style of API:

- Researchers have the ability to control their simulation at a fine-grained level.
- It's relatively easy for the TDW development team to add to or modify a single API call without affecting any others.
- It's possible to develop multiple high-level APIs that share common code.

## 2. Wrapper functions, add-ons, and high-level APIs

TDW includes many **wrapper functions** that simplify the usage of commonly used commands. There are also **add-ons** which typically do something on every frame, such as log messages or save images (add-ons will be covered later in the Core Concepts guide).

The TDW team has also developed several **high-level APIs** that constitute more general frameworks for certain types of experiments such as dataset generation; these APIs usually exist in separate repos.

When possible, this documentation will first show you the underlying TDW commands and then the higher-level functions or classes that do the same thing. The most important thing to know is that all of these higher-level calls ultimately return low-level TDW commands; there is nothing in TDW that exists outside of the Command API.

## 3. No imposed metaphors

Commands don't impose any metaphors. It isn't even strictly necessary to have any agents or environments, nor are there limits to how many agents there are, what sort of agents there are, etc. Some examples:

- It's possible to create a physics simulation without any agents or images.
- It's possible to create a physics simulation with a robot agent.
- It's possible to create a non-physics scene with a non-embodied third person camera.

***

**Next: [Scenes](scenes.md)**

[Return to the README](../../../README.md)

***

See also: 

- [Command API](../../api/command_api.md)