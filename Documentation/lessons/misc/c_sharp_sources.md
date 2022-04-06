# C# Source Code for TDW

The public release of TDW contains all Python code, full documentation and binary executable "builds" of the simulation engine for Linux, OSX and Windows.  The C# source code is in a closed-source private repo because it contains non-free third-party code purchased by the TDW development team While it would technically be possible to release the free portion of the C# source code, doing so would involve many technical challenges and legal implications, none of which we've addressed yet.

A fundamental aspect of how we designed TDW is that we don't expect users to need to modify the C# code of TDW. Doing so requires significant low-level programming experience with Unity and advanced C# development in general. It most cases, it is faster for us to implement new features for you than for you to code them yourself.

That all said, we do recognize that certain users may need to, or want to, make modifications to the underlying C# code to suit specialized use cases. We therefore plan to consider applications for access to the back-end C# source code and Unity project on a case-by-case basis.  If you feel you absolutely need the C# source code for your desired use case of TDW, then before applying please read carefully the **Technical Requirements and Prerequisites FAQ**  section below.  Please make sure that you a) meet the requirements as outlined regarding Unity and C# development experience (we cannot support non-experts using the C# code); and b) understand and accept that we may be much slower to respond to code contributions or queries on this repo compared to the public one, due to our constrained engineering resources.

If after reading  the FAQ you still feel your use case will require access to the underlying C# code, apply for access by contacting Jeremy Schwartz at [jeremyes@mit.edu](mailto:jeremyes@mit.edu) , describing your use case and why you feel it necessary to have access. We will be happy to discuss your situation with you and will fully consider your application.

Please note that access to the TDW C# source code does NOT include access to the "Full" 3D model library, as described on the TDW web site and [in our documentation](../3d_models/non_free_models.md). We are still exploring the idea of making that model library generally available; you can help us understand the level of interest in the library by taking the [brief survey on our web site.](https://docs.google.com/forms/d/e/1FAIpQLSeJGR_PXlVRwOis9dcM2SDwP3Jcuf78Yo0TLmgLWLpuQI9Xig/viewform)

## Technical Requirements and Prerequisites FAQ

### "What experience do I need?"  
Your experience should include most, if not all, of the following:

- **Unity**
  - Component-based architecture
  - Unity Editor
  - Asset bundles
  - How to optimize for speed in Unity
- **C#**
  - Generic types
  - Asynchronous threads
  - Abstract classes and inheritance
- **Flatbuffer**

## Scenarios Where you DO NOT Need the C# Source Code

#### "I want to use TDW with OpenAI Gym." 
Interfacing TDW with OpenAIGym (or similar RL toolkits) can be done completely through the Python API. This has been done already on several projects.

#### "I want to write my own scene setup tools / use my own custom scene data format" 
There are  many examples in the `tdw` repo of how set up custom environments; [read this for more information](../objects_and_scenes/overview.md).

#### "I need to use custom models." 
[We already support this.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/lessons/3d_models/custom_models.md)

#### "I want to add my own custom streamed scene."
We've deliberately restricted the backend pipeline for creating a TDW-compatible scene to the development team because adding scenes is much more complicated than creating a 3D model and requires 3D content-creation tools and experience. If you have a specific requirement for a custom 3D scene, please contact Jeremy Schwartz ([jeremyes@mit.edu](mailto:jeremyes@mit.edu)) and we can discuss your particular situation.

#### "I want to integrate TDW with ROS."

This is a priority feature for TDW that we are already planning to add.

## Scenarios Where you MAY Need the C# Source Code

#### "I need a new command / I need new output data."
Unless you need wholly new functionality, you can ask us for the command, and we can add it quickly. Our API has a robust and rigorous codebase that requires some prior knowledge to modify and extend. It is also likely that the command you need already exists, or that a group of commands can achieve the behavior you need.

 #### "There is a bug in the C# code."
Please post an [Issue in the repo](https://github.com/threedworld-mit/tdw/issues) and we will fix the bug as soon as possible.

***

[Return to the README](../../../README.md)
