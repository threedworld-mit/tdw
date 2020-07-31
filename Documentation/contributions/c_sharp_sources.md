# C# Source Code for TDW

The public release of TDW contains all Python code, full documentation and binary executable "builds" of the simulation engine for Linux, OSX and Windows.  However we have chosen not to release the C# source code for the TDW back-end and other underlying aspects of the platform. Our reasoning is this: TDW has been carefully designed so that the vast majority of use-cases should not require access to any back-end components of the platform. The Python code has been designed so any researcher can work with it easily, and so we can easily support it and accept contributions. The underlying C# components of TDW, on the other hand, require significant low-level programming experience with Unity and advanced C# development in general. 

In summary, we hope and expect that most users will be able to get full value from TDW using the publicly released Python code and simulation engine executables.

However, we do recognize that certain users may need to, or want to, make modifications to the underlying C# code to suit specialized use cases. We therefore plan to consider applications for access to the back-end C# source code and Unity project on a case-by-case basis.  If you feel you absolutely need the C# source code for your desired use case of TDW, then before applying please read carefully the **Technical Requirements and Prerequisites FAQ**  section below.  Please make sure that you a) meet the requirements as outlined regarding Unity and C# development experience (we cannot support non-experts using the C# code); and b) understand and accept that we may be much slower to respond to code contributions or queries on this repo compared to the public one, due to our constrained engineering resources.

If after reading  the FAQ you still feel your use case will require access to the underlying C# code, apply for access by contacting Jeremy Schwartz at [jeremyes@mit.edu](mailto:jeremyes@mit.edu) , describing your use case and why you feel it necessary to have access. We will be happy to discuss your situation with you and will fully consider your application.

Please note that access to the TDW C# source code does NOT include access to the "Full" 3D model library, as described on the TDW web site and [in our documentation](https://github.com/threedworld-mit/tdw/blob/v1.6.0.4/Documentation/misc_frontend/models_full.md). We are still exploring the idea of making that model library generally available; you can help us understand the level of interest in the library by taking the [brief survey on our web site.](https://docs.google.com/forms/d/e/1FAIpQLSeJGR_PXlVRwOis9dcM2SDwP3Jcuf78Yo0TLmgLWLpuQI9Xig/viewform)

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
The TDW Python API can handle a very broad range of scene setup scenarios, both procedural and explicitly scripted, including parsing custom data formats There are a number of examples of how to set up scenes in our Example Controllers, including deserializing JSON files containing scene setup data. Our [Rube Goldberg Demo](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/rube_goldberg.md) is a good example of this; while the controller does make use of "non-free" models, the scene setup logic used is the important point here.

#### "I need to use custom models." 
[We already support this.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/add_local_object.md)

#### "I want to add my own custom streamed scene."
We've deliberately restricted the backend pipeline for creating a TDW-compatible scene to the development team because adding scenes is much more complicated than creating a 3D model and requires 3D content-creation tools and experience. If you have a specific requirement for a custom 3D scene, please contact Jeremy Schwartz ([jeremyes@mit.edu](mailto:jeremyes@mit.edu)) and we can discuss your particular situation.

## Scenarios Where you MAY Need the C# Source Code

#### "I want to integrate TDW with ROS / URDF."
This does require access to the C# source code and Unity project. However integrating with robotic motion control systems and importing URDF format files, with a view towards supporting transfer to real-world robot arms, is high up on our development agenda.  We are open to discussing our plans and progress on this with you.

#### "I want to add support for the Leap Motion VR controller."
This does require access to the C# source code and Unity project, as well as the relevant Leap Motion VR developer libraries.  We have worked with Leap Motion VR in the past, in TDW, and can discuss what is involved in supporting it.

#### "I need a new command / I need new output data."
Unless you need wholly new functionality, you can ask us for the command, and we can add it quickly. Our API has a robust and rigorous codebase that requires some prior knowledge to modify and extend. It is also likely that the command you need already exists, or that a group of commands can achieve the behavior you need.

 #### "There is a bug in the C# code."
Please post an [Issue in the repo](https://github.com/threedworld-mit/tdw/issues) and we will fix the bug as soon as possible.

## Final Word

Even if your project does require access to the TDW back-end and C# source code, and you have the necessary skills, it’s important to discuss your project requirements with us first before contemplating a major development effort, because:

- We may already be working on developing what you need, or it may be on our near-term development road map. In either case we can discuss with you when we think that development effort could be completed, and perhaps discuss collaborating with you to speed up the development

- If your requirement is NOT on our roadmap, it may be something we could develop quite quickly, in which case we could look at adding it to our near-term development queue

- If is NOT something we can do in the near-term, nor are we planning to do it, we may still be able to offer advice on how to proceed, and/or offer recommendations for third-party code plugins that could accelerate your development
