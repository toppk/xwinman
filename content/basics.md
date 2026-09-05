---
title: The Basics
---

## The Basics

This section covers some basic concepts, and includes information on how to
install and change window managers. It follows on from the
[introduction](intro.html) so you may like to read that first if you haven't
already.

### Virtual Desktops and Workspaces

As computers are used for such a variety of purposes it makes sense not to
have all the windows of all currently running applications on the screen at
once, as this can soon get awkward and confusing. Virtually all windowing
systems allow you to **iconify** windows, which shrinks them down to a small
icon, ready for when you need the application again. But some window managers
also provide the ability to separate windows and tasks in other ways.

The first approach uses the concept of a **virtual desktop.** This is like
having lots of different screens, but all of them can be displayed on your
single monitor. These screens can be used to spread out your windows, to
prevent clutter. You can move around this grid of screens in various ways,
depending on the window manager, and how it is set up. Window managers often
provide a **pager** as well, which is a small diagram of all the screens of
the virtual desktop, containing representions of the windows currently open.

Similar to virtual desktops is the concept of **workspaces.** This involves
having multiple, distinct screens, where the intention is for you to group all
related windows on one screen, called a workspace. For example you may have a
workspace for handling e-mail, one for news, one for word processing, and so
on. The window manager often provides a group of buttons, one for each
workspace, which are used to select the current workspace.

### Changing Window Manager

Obviously if you want to try different window managers you need to know how to
change the default window manager. You can't just run it from the command
line, as it will complain that there is already a window manager running.
However, how you change the window manager is dependent on how your system is
set up, and the particular implementation and version of X you are using. The
most common scenarios are covered below.

#### Running X from the command line, using "startx" or "xinit"

The <kbd>xinit</kbd> command is the one which actually starts the X Window System, but
it usually needs certain options, which is where the <kbd>startx</kbd> command comes in.
It is simply a shell script which sets up variables, performs any other tasks
specific to the local system, and then calls <kbd>xinit</kbd>. Therefore you should use
<kbd>startx</kbd> in preference to <kbd>xinit</kbd> if it is available.

There is a system configuration file that <kbd>startx</kbd> uses, and a user's own
configuration file that is used in preference to the system one, if it exists.
You can find out the names of these files by looking at the <kbd>startx</kbd> script.
(You can find out where the script is by doing "<kbd>which startx</kbd>".) The system
configuration file is usually something like <kbd>/etc/X11/xinit/xinitrc</kbd> and the user
configuration file is virtually always <kbd>.xinitrc</kbd> in the root of your home
directory. Look at the system file and see where it calls the default window
manager. To change window managers for yourself, either copy this file to
<kbd>\~/.xinitrc</kbd> and edit it appropriately, or create your own from scratch. It should
end with "exec windowmanager" and any commands before that which don't finish
quickly should be run in the background. Here's a simple example:

<pre>
     #!/bin/sh
     xterm &
     exec fvwm
	 </pre>

The first line selects the program used to run the script itself. Without this
your default shell will be used. The second line runs an <kbd>xterm</kbd> in the
background, and the third line runs the window manager. The <kbd>exec</kbd> command
is used to replace the script process with the process of the window manager
itself. This is because X shuts down when the script finishes running, but if
the window manager replaces it, it will shut down when the window manager
quits instead, which is usually the desired behaviour.

You can see this for yourself if you change the first line to "<kbd>exec xterm</kbd>". The
window manager will then not be started and X will shut down when you exit the
xterm window. This is also an interesting experience is it illustrates exactly
what a window manager does, and what X does itself. Without a window manager
running you can still run programs, and bring up windows, but they don't have
any decorations and you can't move them.

#### Running X from a graphical login box, such as with XDM

XDM is the X Display Manager. It starts X when the machine boots up, and then
provides a graphical login box instead of the command line, so that when users
come and go they don't have to keep starting and quitting X. To configure the
setup in this case is similar to that of above, but the user file is now
<kbd>\~/.xsession</kbd> and the system file something like <kbd>/etc/X11/xdm/Xsession</kbd>.

**Caution:** if you're using <kbd>startx</kbd> as above and something goes wrong with
the invocation of the window manager you will drop back to the command line
and can fix it from here, but if you're using XDM and the same happens, you'll
drop back to the login box, without having the chance to fix it. So if you are
editing your <kbd>\~/.xsession</kbd> file, particularly if you're trying a new window manager
for the first time, make sure that either you're logged in elsewhere, and can
edit the <kbd>\~/.xsession</kbd> file from there, or you use the "<kbd>exec xterm</kbd>" approach above,
and start the window manager from within the <kbd>xterm</kbd>, and only change the
<kbd>\~/.xsession</kbd> file when you're sure it works okay.

#### Running X from the CDE graphical login

If you log in with this you will get the CDE (Common Desktop Environment),
which uses the DTWM window manager. If you don't want this you can select
"Command line login" from the options menu. You should then be able to follow
the first scenario above.

Alternatively, you can use the "wmStartupCommand" resource to use a different
window manager inside the CDE itself. For example to use fvwm you can have the
following in your <kbd>\~/.Xdefaults</kbd> file:

<pre>
     *wmStartupCommand: /usr/X11R6/bin/fvwm
     *waitWmTimeout: 2
	 </pre>

Then when fvwm exits it should call:

<pre>
     /usr/dt/bin/dtaction ExitSession 
	 </pre>

to tell CDE to end the session. For more info see the [FVWM
FAQ.](http://www.fvwm.org/generated/FAQ.html)

### Installing a Window Manager

First of all, you **don't** need to be root to install a new window manager.
All you need is enough disk space for the source distribution with room to
unpack and then compile it. You may also need some libraries, such as
[XPM](http://www.inria.fr/koala/lehors/xpm.html), if they are not already on
your system.

Here are the main steps involved:

1.  Download and unpack the distribution. (Tip: if the file is called
    <kbd>wm.tar.gz</kbd>, you can unpack this in one go with "<kbd>gzcat wm.tar.gz | tar -tf -</kbd>". If you haven't
    got <kbd>gzcat</kbd>, try "<kbd>gzip -cd</kbd>" instead).
2.  If you've been able to find a binary for your platform, then you're
    sorted. Simply copy it and any other required files to wherever you want
    them, (or where the instructions tell you to put them), and then change
    from the default window manage to it, as detailed above.
3.  No binary, so we're going to have to compile the window manager ourselves.
    First you need to generate a makefile for your platform. This is usually
    done with either "<kbd>xmkmf;
		  make Makefiles</kbd>" or "<kbd>./configure</kbd>", but **read the instructions**
    for the precise steps required. Most packages come with both a <kbd>README</kbd>
    and an <kbd>INSTALL</kbd> file, and are there solely for your benefit.
4.  To actually perform the compilation process, the "<kbd>make</kbd>" command is
    usually run. This calls the compiler for each source code file, and then
    calls the linker to create an executable. Most window managers consist of
    many thousands of lines of code, so this can take a while. This is also
    the step most likely to go wrong. It could fail to find some include files
    or libraries, which to may need to refer to explicitly in the <kbd>Imakefile</kbd>, or
    sometimes a <kbd>config.h</kbd> file. Or the window manager may not have been tested
    on your platform, and could need detailed knowledge of the platform to get
    working. If you get completely stuck you could see if anyone on the
    [comp.windows.x](news://comp.windows.x) newsgroup can help.
5.  Assuming the compilation process does actually complete successfully, you
    then need to install the window manager and any associated files. You
    could copy the files to suitable locations yourself if you can see which
    ones are required. If you do have root access, "<kbd>make install</kbd>" will usually do
    it for you, although it is a good idea to do "<kbd>make -n install</kbd>" first, which will
    show you the steps it would take, without actually performing them. If you
    don't have root access, you'll need to change the directories used to ones
    in your home directory if you want to perform this step. This can usually
    be done in the <kbd>Imakefile</kbd> or <kbd>config.h</kbd>, but again **read the instructions**
    for the particular window manager in question.

That's it. Good luck!
