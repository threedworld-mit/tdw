**Technical Requirements and Prerequisites For TDW Backend Code Access Please Read Carefully Before Applying for Access**

 

If you feel you need access to TDW’s C# backend code and Unity project for your use case, please read this document thoroughly before contacting us to apply for access.  We have gone to great lengths to make the public version of TDW usable across a very broad range of use cases, without requiring access to the backend components of TDW.

 

Necessary Experience – your experience should include most, if not all, of the following:

·       **Unity**

o   Component-based architecture

o   Unity Editor

o   Asset bundles

o   How to optimize for speed in Unity

·       **C#**

o   Generic types

o   Asynchronous threads

o   Abstract classes and inheritance

·       **Flatbuffer**

 

**Scenarios Where you DO NOT Need C# Sources**

 

**“I want to use TDW with OpenAI Gym.”**

Interfacing TDW with OpenAIGym (or similar RL toolkits) can be done completely through the Python API. This has been done already on several projects.

 

**“I want to write my own scene setup tools / use my own custom scene data format”**

The TDW Python API can handle a very broad range of scene setup scenarios, both procedural and explicitly scripted, including parsing custom data formats There are a number of examples of how to set up scenes in our Example Controllers, including deserializing JSON files containing scene setup data. Our [Rube Goldberg Demo](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/rube_goldberg.md) is a good example of this; while the controller does make use of “non-free” models, the scene setup logic used is the important point here.

 

**“I need to use custom models.”** 

[We already support this.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/add_local_object.md)

 

**“I want to add my own custom streamed scene.”**

We've deliberately restricted the backend pipeline for creating a TDW-compatible scene to the development team because adding scenes is much more complicated than creating a 3D model and requires 3D content-creation tools and experience. If you have a specific requirement for a custom 3D scene, please contact Jeremy Schwartz ([jeremyes@mit.edu](mailto:jeremyes@mit.edu)) and we can discuss your particular situation.

 

  

**Scenarios Where you MAY Need C# Sources**

 

**“I want to integrate TDW with ROS / URDF.”** This does require access to the C# sources and Unity project. However integrating with robotic motion control systems and importing URDF format files, with a view towards supporting transfer to real-world robot arms, is high up on our development agenda.  We are open to discussing our plans and progress on this with you.

 

**“I want to add support for the Leap Motion VR controller.”**

This does require access to the C# sources and Unity project, as well as the relevant Leap Motion VR developer libraries.  We have worked with Leap Motion VR in the past, in TDW, and can discuss what is involved in supporting it.



**"I need a new command / I need new output data"**
 Unless you need wholly new functionality, you can ask us for the command, and we can add it quickly. Our API has a robust and rigorous codebase that requires some prior knowledge to modify and extend. It is also likely that the command you need already exists, or that a group of commands can achieve the behavior you need.
 
 **"There is a bug in the C# code"**
 Please post an [Issue in the repo](https://github.com/threedworld-mit/tdw/issues) and we will fix the bug as soon as possible.

 



**Final Word**

Even if your project does require access to the TDW back-end and C# sources, and you have the necessary skills, it’s important to discuss your project requirements with us first before contemplating a major development effort, because:

·       We may already be working on developing what you need, or it may be on our near-term development road map. In either case we can discuss with you when we think that development effort could be completed, and perhaps discuss collaborating with you to speed up the development

·       If your requirement is NOT on our roadmap, it may be something we could develop quite quickly, in which case we could look at adding it to our near-term development queue

·       If is NOT something we can do in the near-term, nor are we planning to do it, we may still be able to offer advice on how to proceed, and/or offer recommendations for third-party code plugins that could accelerate your development

 