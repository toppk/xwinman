---
title: AfterStep
build:
  publishResources: false
logo_sm:
  file: afterstep_sm.gif
  alt: afterstep
  width: 104
  height: 32
logo:
  file: afterstep.gif
  alt: '[AfterStep]'
  width: 203
  height: 62
license: GPL
activity: High
---

AfterStep is based on Fvwm, but it is designed to emulate some of the look and
feel of the NEXTSTEP® user interface, while adding useful, requested, and neat
features. It started life under the name of Bowman, by Bo Yang, but has since
moved past simple emulation and into a niche as its own valuable window
manager.

Major changes from Fvwm are:

1.  NeXTSTEP-alike title bar, title buttons, borders and corners.
2.  AfterStep's Wharf is a much worked-out version of Fvwm's GoodStuff. To
    avoid copyright complications it is not called a "dock."
3.  NeXTSTEP style menu. However the menus are not controlled by applications,
    they are more of pop-up service lists on the root window.
4.  NeXTSTEP style icons. These styles are hard-coded in the program, thought
    to be good for a consistent look of NeXTSTEP interface.

However, the flexibility of Fvwm was not traded off. The initiation file,
.steprc, recognizes most of the fvwm( 1.24r) commands. Virtual screen and
pagers are still intact. Fvwm modules should work just fine. However,
compatibility with Fvwm-2 is not planned.

Here are some example configuration files, with screenshots. The configuration
files should be renamed to <kbd>.steprc</kbd> in the top level of your home directory,
except for the now out-dated bowman configuration.

{{< contributions 1 >}}

[The Official AfterStep HomePage](http://www.afterstep.org/) contains a wealth
of information including more screenshots, precompiled binaries, and some nice
icons. It also contains the latest version of AfterStep, which has now
advanced considerably from its previous incarnation as Bowman.

Other AfterStep related pages include:

{{< links 1 >}}

There are several small applications available which are designed to be
swallowed into a Wharf bar. These include ASMail, which is a mail-checker like
xbiff, ASModem, which displays the status of your modem, and ASCD, a fully
functional CD Player. They are all available from the "AfterStep applets" page
listed above.

There is a replacement library for libXaw, called
[neXtaw](http://siag.nu/neXtaw/), which attempts to emulate the look and feel
of the NeXTSTEP desktop. It is based on the popular
[Xaw3d](ftp://ftp.x.org/contrib/widgets/Xaw3d/) library which gives standard
Athena widgets a 3D look. Also of interest is
[ascp,](http://hubble.colorado.edu/~nwanua/htmldir/ascp.html) the AfterStep
ControlPanel, which is a graphical tool for configuring AfterStep. It was
originally written using Tcl, but has since been converted to use GTK+
widgets.
