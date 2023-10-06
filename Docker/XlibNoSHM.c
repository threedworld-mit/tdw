/*
 * Fake MIT-SHM lib found at https://github.com/mobdata/mobnode/blob/01fa78f67f01ade55b3dd6c4d8da088ed9507f9c/XlibNoSHM.c
 * Slightly adjusted following tips of @joanbm here: https://github.com/jessfraz/dockerfiles/issues/359#issuecomment-1015835732
 * Used by x11docker in some x11docker/xserver setups and for option --hostdisplay.
 */

/*
 * Firefox47 and above has a "bug":
 *   https://bugzilla.mozilla.org/show_bug.cgi?id=1271100
 * Firefox attempts to use the X (X11, X-windows) extension MIT-SHM.
 * It is "known" that MIT-SHM can only work on "local" displays. However:
 *  - some X servers report supporting MIT-SHM even on remote (e.g.
 *    TCP-connected) displays. (Maybe "right" so not a bug: the client
 *    might have access to the X server machine.)
 *  - the ssh "port forwarding" feature makes both the X server and client
 *    appear to be "local" (somewhat: using TCP localhost, not Unix domain
 *    sockets); and ssh makes no attempt to intercept or disable MIT-SHM.
 * To work around this confusion, when we know MIT-SHM should not be used,
 * (in the client application) we fudge the returns of the
 *   XQueryExtension
 *   XListExtensions
 *   XShmQueryExtension
 *   XShmQueryVersion
 * to "hide" the MIT-SHM extension.
 * (Firefox48 only uses XQueryExtension, others for future robustness.)
 *
 * Firefox already has code to detect when MIT-SHM is not working, but that
 * does not seem reliable enough. Maybe in future (from FF50 or 51) it will
 * use XCB instead of Xlib and then its detection will work better; if not,
 * a similar workaround will be needed.
 *
 * May need to explicitly mention /usr/lib/libdl.so in LD_PRELOAD
 * (or could or should it be /lib/libdl-2.11.3.so ?), otherwise ...?
 *
 * Compile and build library:
	gcc -shared -o XlibNoSHM.so XlibNoSHM.c
 * to be used with
 *   LD_PRELOAD='/lib/x86_64-linux-gnu/libdl.so.2:./XlibNoSHM.so' firefox
 */

#include <stdio.h>
#include <string.h>
#include <X11/Xlib.h>
#include <dlfcn.h>
#define LIBXLIB "libXext.so.6"

Bool XQueryExtension(Display* dpl, _Xconst char* name, int* major, int* event, int* error)
{
  static Bool (*original_XQueryExtension)(Display*, _Xconst char*, int*, int*, int*) = NULL;

  /* printf("Got XQueryExtension %s\n",name); */
  if (!strcmp(name,"MIT-SHM")) {
    /* printf("Returning False for XQueryExtension %s\n",name); */
    *major = 0;
    return False;
  }
  if (!original_XQueryExtension) {
    void *handle = dlopen(LIBXLIB, RTLD_LAZY);
    if (!handle) return False;
    original_XQueryExtension = dlsym(handle, "XQueryExtension");
    if (!original_XQueryExtension) return False;
  }
  /* printf("Doing original_XQueryExtension ...\n"); */
  return original_XQueryExtension(dpl, name, major, event, error);
}

char** XListExtensions(Display* dpl, int* nexts)
{
  static char** (*original_XListExtensions)(Display*, int*) = NULL;
  char** extNames;
  int i;

  /* printf("Got XListExtensions\n"); */
  if (!original_XListExtensions) {
    *nexts = 0;
    void *handle = dlopen(LIBXLIB, RTLD_LAZY);
    if (!handle) return NULL;
    original_XListExtensions = dlsym(handle, "XListExtensions");
    if (!original_XListExtensions) return NULL;
  }
  /* printf("Doing original_XListExtensions ...\n"); */
  extNames = original_XListExtensions(dpl, nexts);

  if (extNames && *nexts > 0) {
    for (i = 0; i < *nexts; ++i) {
      if (extNames[i] && !strcmp(extNames[i],"MIT-SHM")) {
        /* printf("Replacing MIT-SHM by No-... in XListExtensions output\n"); */
        (void)strncpy(extNames[i],"No-",3);
      }
    }
  }

  return extNames;
}

Bool XShmQueryExtension(Display* display)
{
  /* printf("Returning False for XShmQueryExtension\n",); */
  return False;
}

Bool XShmQueryVersion(Display *display, int *major, int *minor, Bool *pixmaps)
{
  /* printf("Returning False for XShmQueryVersion\n",); */
  return False;
}
