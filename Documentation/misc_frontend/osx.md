# TDW and OS X

There are a few common problems users experience when running TDW on OS X. Here are the known solutions:

## "I can't run the .app"

There are two ways to run the .app of the build, each of which has a different solution:

### Running the .app in the shell

You might want to run the .app in the shell to utilize [command-line arguments](../getting_started.md). 

As with all OS X programs, the .app can't be directly opened in the shell. Instead:

1. Click right on the .app file
2. Click on Show Package Contents 
3. Find the executable in the MacOS folder (e.g.  “TDW_v1.5.0”) and drag that to your bash shell window.

### Double-clicking the .app

If you aren't using command-line arguments, you can double-click and run the .app like any other.

## "When I double-click TDW.app I get an error: `TDW.app is damaged and can't be opened`"

This is a [known Unity bug](https://issuetracker.unity3d.com/issues/macos-builds-now-contain-a-quarantine-attribute) and it will occur if you download the build from TDW's releases page. To fix it, run `setup.sh` (located in the same directory as `TDW.app`).

## "I'm receiving `localhost` errors"

The build might fail to do anything because `localhost` isn't a listed host. In Unity Editor, you'll see an error like this:

```
SocketException: Could not resolve host 'localhost'
System.Net.Dns.Error_11001 (System.String hostName) (at <0079a30f96a047348857e1cecc6c638a>:0)
System.Net.Dns.GetHostByName (System.String hostName) (at <0079a30f96a047348857e1cecc6c638a>:0)
System.Net.Dns.GetHostEntry (System.String hostNameOrAddress) (at <0079a30f96a047348857e1cecc6c638a>:0)
NetMQ.Core.Transports.Tcp.TcpAddress.Resolve (System.String name, System.Boolean ip4Only) (at <cd775f2ee43b4afd8cc83c9f5ddee1f4>:0)
NetMQ.Core.SocketBase.Connect (System.String addr) (at <cd775f2ee43b4afd8cc83c9f5ddee1f4>:0)
NetMQ.NetMQSocket.Connect (System.String address) (at <cd775f2ee43b4afd8cc83c9f5ddee1f4>:0)
NetMQ.NetMQSocket..ctor (NetMQ.ZmqSocketType socketType, System.String connectionString, NetMQ.NetMQSocket+DefaultAction defaultAction) (at <cd775f2ee43b4afd8cc83c9f5ddee1f4>:0)
NetMQ.Sockets.RequestSocket..ctor (System.String connectionString) (at <cd775f2ee43b4afd8cc83c9f5ddee1f4>:0)
Req.NetMQClient () (at Assets/TDW/Scripts/Networking/Req.cs:284)
System.Threading.ThreadHelper.ThreadStart_Context (System.Object state) (at <7d97106330684add86d080ecf65bfe69>:0)
System.Threading.ExecutionContext.RunInternal (System.Threading.ExecutionContext executionContext, System.Threading.ContextCallback callback, System.Object state, System.Boolean preserveSyncCtx) (at <7d97106330684add86d080ecf65bfe69>:0)
System.Threading.ExecutionContext.Run (System.Threading.ExecutionContext executionContext, System.Threading.ContextCallback callback, System.Object state, System.Boolean preserveSyncCtx) (at <7d97106330684add86d080ecf65bfe69>:0)
System.Threading.ExecutionContext.Run (System.Threading.ExecutionContext executionContext, System.Threading.ContextCallback callback, System.Object state) (at <7d97106330684add86d080ecf65bfe69>:0)
System.Threading.ThreadHelper.ThreadStart () (at <7d97106330684add86d080ecf65bfe69>:0)
UnityEngine.UnhandledExceptionHandler:<RegisterUECatcher>m__0(Object, UnhandledExceptionEventArgs)
```

To add `localhost` to your computer's list of hosts, read [this](https://apple.stackexchange.com/a/307029).

## "I can't use NVIDIA Flex"

[Flex](flex.md) doesn't work on OS X.

