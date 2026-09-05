---
title: Setting Resources
url: /resource.html
build:
  publishResources: false
---

## Setting Resources

**Note:** This section describes the general mechanism used to configure X
programs. It doesn't relate specifically to window managers, and more recent
trends mean that programs usually provide their own means of configuration,
often using a GUI. Therefore knowing the details of X resource setting is less
useful now than it used to be.

X programs can be customized by using resources. These resources can be
specified in many different places. In order of increasing priority these
include:

1.  Fallback resources programming into the application.
2.  Library resource files controlled with <kbd>XFILESEARCHPATH</kbd> variable.
3.  User resource files controlled with <kbd>XUSERFILESEARCHPATH</kbd>, and <kbd>XAPPLRESDIR</kbd> variables.
4.  X resource database, loaded with xrdb.
5.  X resource default files, <kbd>$HOME/.Xdefaults</kbd> or <kbd>$HOME/.Xresources</kbd>.
6.  Standard command line options.
7.  Hardcoded resources, set within the program.

Options nearer the end of the list override ones further up the list. For
personal customization of X programs, the best method to use is a single
<kbd>$HOME/.Xresources</kbd> file (<kbd>$HOME/.Xdefaults</kbd> will probably also work, but is now obsolete). This file
gets read when you start X. If you have a lot of resources to set for a
particular program, or you have your own version of an X program with a
resource file, it would be best to create a directory for these files. This
directory would be searched when an X program is started. These two methods
are discussed in more detail below.

### The .Xresources file

The simpliest and best way to customize X programs is to create a file called
<kbd>.Xresources</kbd> in the top level of your home directory.

Any line beginning with a <kbd>!</kbd> is ignored, so can be used for comments.
Each resource specification appears on a separate line and is often of the
form <kbd>Client\*resource:
	value</kbd>. The client name is specified by the program, but unless stated
otherwise, this is usually the name of the program with the first letter
capitalized, e.g. netscape becomes <kbd>Netscape</kbd>, unless the first letter is an
<kbd>X</kbd>, in which case the first two letters are capitalized, e.g. xterm
becones <kbd>XTerm</kbd>. The resource name is usually a single string, such as
<kbd>scrollBar</kbd>. After the colon, and any whitespace, comes the value you wish to set
the resource to. This is always a string, which gets converted into the
correct type. So an example of a complete specification is <kbd>XTerm\*scrollBar: True</kbd>. This
would cause all xterms to have a scrollbar.

The resource field of the specification can actually be preceded by a path
through the widget hierarchy. In the specification <kbd>XTerm.vt100.geometry: 80x25</kbd>, the geometry
resource is only specified for the vt100 widget of the xterm, which is the
main text area. If <kbd>XTerm\*geometry: 80x25</kbd> was used instead, all widgets, such as the menus
which popup with Control-Mouse button combinations, would be given the same
geometry as the main text area. Notice that in the first case, the fields were
separated by "<kbd>.</kbd>", and not "<kbd>\*</kbd>". This causes the widget you are
setting the resource of to be specified exactly, whereas the "<kbd>\*</kbd>" means
"any route through the widget hierarchy." Any combination for "<kbd>.</kbd>" and
"<kbd>\*</kbd>" can be used in a resource specification.

The order of resource specifications in a file does not matter, as long as
they do not conflict. If they do, a warning is usually given, and the one that
appears last in the file is used. However the same resource can be specified
twice if the generality of the specifications is different. For example
<kbd>Maker\*background: gray70</kbd> would change the background colour of all widgets (unless overridden
later) to be gray70. However, <kbd>Maker\*vertSB.background: gray65</kbd> could be used to change the background
colour of all vertical scrollbars. Thus, the more specific resource is
overriding the more general one.

Another way of specifying widgets is to name a particular class. For example,
<kbd>Editres\*Command.background:
	yellow</kbd> would set all widgets of class commandWidgetClass, that is normal
buttons, to have a yellow background.

Examine this [example .Xresources](rc/Xresources) file. It demonstates valid
resource specifications in more detail, and may contain some useful options
for various programs.

Your .Xresources file may be processed when your start your X session. If not,
add <kbd>xrdb -merge \~/.Xresources</kbd> to an X login script such as <kbd>\~/.xinitrc</kbd>. If you edit the resource
file and you want the changes to take effect during the current X session, you
can parse it by executing: <kbd>xrdb -merge \~/.Xdefaults</kbd>.

### User resource files

You can also have a directory of resource files, with one file per program. To
do this, create the directory, say <kbd>$HOME/appres</kbd>, and then set the environment
variable <kbd>XAPPLRESDIR</kbd> to point to it. So you would have something like <kbd>setenv XAPPLRESDIR $HOME/appres/</kbd> in
your <kbd>.cshrc</kbd> file,if your shell is csh or tcsh.

Now, when you start an X program, this directory will be searched for a file
with the same name as the resource name of the program. This is the client
name used in .Xdefaults files. This file can contain identical specifications,
but the client name is optional. For example, a file called <kbd>XTerm</kbd> could
contain the line <kbd>\*background: deepskyblue</kbd>.

### Standard Options

Applications should document any specific resources that can be used with the
program, but there are many standard options which can be used with virtually
all X programs. These include:

- <kbd>display</kbd> - the X server to use
- <kbd>geometry</kbd> - the size and location
- <kbd>background</kbd>, or <kbd>bg</kbd> - background colour
- <kbd>bordercolor</kbd>, or <kbd>bd</kbd> - colour to use for borders
- <kbd>foreground</kbd>, or <kbd>fg</kbd> - foreground colour
- <kbd>font</kbd>, or <kbd>fn</kbd> - the font to use for displaying text
- <kbd>iconic</kbd> - the program should be initially iconified
- <kbd>name</kbd> - the name under which resources should be found
- <kbd>title</kbd> - the title for the program window
- <kbd>xrm</kbd> - specifies a resource name and value

For more details, see the man page for X.
