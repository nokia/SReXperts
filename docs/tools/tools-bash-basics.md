---
tags:
  - Linux
  - Command line
  - bash
  - cat
  - echo
  - grep
  - tail
  - vi
  - vim
---

# Linux/UNIX shell basics

This page is not an activity to follow, but rather a very small reference guide to some common UNIX/Linux commands that may come in useful during the activities in case using the `bash` Linux/UNIX shell is new to you.

In this page we have at your disposal some useful **bash tips** for managing files in the Linux/UNIX shell (CLI).
You can review how to read a file, search for a string on the file, replace a string and some other handy hints.

## `cat`

The `cat` command in Linux displays a files contents. It reads one or more files and prints their content to the terminal. `cat` can be used to view file contents, combine files, and create new files.

### Basic usage

/// tab | Syntax
```
cat [option] [filename]
```
///

Now let’s go on to some practical examples of using `cat`. To better understand the results, a simple text file has been created.  The file contains the following lines:

/// tab | Contents of `testfile`
```
Hi 
this 
is test file 
to carry out a few 
operations with cat 
123 456 
Abcd 
ABCD 
```
///

### Print content to the terminal

/// tab | Command
```
cat testfile 
```
///
/// tab | Output
```
Hi 
this 
is test file 
to carry out a few 
operations with cat 
123 456 
Abcd
ABCD
```
///

### Print content to the terminal with line numbers

/// tab | Command
```
cat -n testfile 
```
///
/// tab | Output
```
     1  Hi
     2  this
     3  is test file
     4  to carry out a few 
     5  operations with cat
     6  123 456
     7  Abcd
     8  ABCD
```
///


## `echo`

The `echo` command is a built-in command generally used to display the text or message on the screen.  The `echo` command can also be used to write text to a file or to append a new line of text to a file.

### Basic usage

/// tab | Syntax
```
echo [option]
```
///

The following is a simple example for the `echo` command.

/// tab | Command
```
echo Hello World!
```
///
/// tab | Output
```
Hello World!
```
///

There are three common options:

- `-n`: Does not print the trailing newline.
- `-E`: Is the default option that disables the implementation of escape sequences.
- `-e`: Is used to enable interpretation of backslash escape characters.

/// note
Your shell may have its own version of `echo`, which will supersede the version described here.  Please refer to your shell's documentation for details about the options it supports.
///

### Escape sequences

Some escape sequences perform different operations such as:

- `\\`: Backslash
- `\n`: New Line
- `\r`: Carriage Return
- `\t`: Horizontal Tab


/// note
Depending on your Operating System (OS) (Windows, Linux or MacOS) the new line on a file is different:

- **Windows**: `\r\n`
- **Linux**: `\n`
- **MacOS**: `\n\r`
///

#### Example 1: Backslash

/// tab | Command
```
echo -e "Hackathon\\For\\SreXperts"
```
///
/// tab | Output
```
Hackathon\For\SreXperts
```
///

#### Example 2: New Line

/// tab | Command
```
echo -e "Hackathon\nFor\nSreXperts"
```
///
/// tab | Output
```
Hackathon
For
SreXperts
```
///

#### Example 3: Carriage Return

/// tab | Command
```
echo -e "Hackathon\rFor SreXperts"
```
///
/// tab | Output
```
For SreXperts
```
///

#### Example 4: Horizontal Tab

/// tab | Command
```
echo -e "Hackathon\tFor\tSreXperts"
```
///
/// tab | Output
```
Hackathon       For     SreXperts
```
///

## Redirect output to a file

One of the lesser known functionalities of the bash terminal is the ability to redirect the output from the terminal into a file. You can use `command > file` to create a file with the content of the standard output (where `command` is the shell command that generates the output and `file` is the name of the destination file).

The `>` symbol is used to redirect the output of a command to a file instead of the terminal screen.

### Example: Write `echo` output to a file

/// tab | Command
```
echo "Hackathon For SreXperts" > test.txt
```
///

To print the contents of the file we just created, use the `cat` command.

/// tab | Command
```
cat test.txt
```
///
/// tab | Output
```
Hackathon For SreXperts
```
///

## Appending output to a file

In addition to the "redirect to a file" function, Linux shell's allow the user to append (or add) data to an existing file.

The `>>` symbol is used to append the output of a command to a file instead of the terminal screen.

### Example: Append the output of the `echo` command to an existing file

/// tab | Command
```
echo "SreXperts is the best" >> test.txt
```
///

To print the contents of the file we just appended to, use the `cat` command.

/// tab | Command
```
cat test.txt
```
///
/// tab | Output
```
Hackathon For SreXperts
SreXperts is the best
```
///


## `grep`

The `grep` command is among the system administrator’s “Swiss Army knife” set of tools.  It is extremely useful to searching for strings and patterns in a file, a group of files or hierarchical directory structure. 

This section introduces the basics of `grep`, provides examples of some more advanced uses and provides links for further reading.

`grep` (an acronym for “Global Regular Expression Print”) is installed by default on almost every distribution of Linux.

### Basic usage

`grep` finds a string in a given file or input, quickly and efficiently. While most everyday uses of the command are simple, there are a variety of more advanced uses that most people don’t know about, including regular expressions and more, which can become quite complicated.

/// tab | Syntax
```
grep [option] [regexp] [filename]
```
///


Now let’s see some practical examples of the `grep` command. 

To better understand the results, a simple text file has been created.  The file contains the following lines:

/// tab | Contents of `testfile`
```
Hi 
this 
is test file 
to carry out few regular expressions 
practical with grep 
123 456 
Abcd
ABCD
```
///

### Case-insensitive search

The `-i` option allows searches to be case insensitive.

/// tab | Command
```
grep -i 'abcd' testfile 
```
///
/// tab | Output
```
Abcd 
ABCD
```
///

### Whole-word search

The `-w` option requires that the whole word is matched.

/// tab | Command
```
grep -w 'test' testfile 
```
///
/// tab | Output
```
is test file
```
///

### Inverted search

The `-v` option inverts the search, for example, matching on `practical` would return lines containing `practical` but the *inverted* search would return lines **not** containing `practical`.

/// tab | Command
```
grep -v 'practical' testfile 
```
///
/// tab | Output
```
Hi 
this 
is test file 
to carry out few regular expressions 
123 456 
Abcd 
ABCD
```
///

### Print lines after match

The `-A` option, when provided with a number, allows the searches to provide some context by additionally printing the requested number of lines after each match is found.

/// tab | Command
```
grep -A 1 '123'  testfile
```
///
/// tab | Output
```
123 456 
Abcd
```
///

### Print lines before match

The `-B` option, when provided with a number, allows the searches to provide some context by additionally printing the requested number of lines before each match is found.

/// tab | Command
```
grep -B 2 'Abcd' testfile
```
///
/// tab | Output
```
practical with grep 
123 456 
Abcd
```
///


### Using `grep` on command outputs with the pipe character

`grep` can also be used to find a string in command output using a pipe (`|`) to feed the standard out (`STDOUT`) of the command to the standard in (`STDIN`) of `grep`.

/// tab | Syntax
```
command | grep [option] [regexp]
```
///

The following example shows how the `cat` and `grep` commands can be chained together using the pipe (`|`) symbol.

/// tab | Command
```
cat testfile | grep -i 'abcd' 
```
///
/// tab | Output
```
Abcd 
ABCD
```
///

## `tail`

The UNIX/Linux `tail` command displays the latest content from the end of a chosen file(s) directly to the screen. This function is useful for instantly viewing recent additions to files, as new information is often appended at the end.

To better understand the results, a simple text file has been created.  The file contains the following lines:

/// tab | Contents of `testfile`
```
Hi 
this 
is test file 
to carry out a few
operations with tail.
The Tail command  
prints the last 
10 lines by default 
so let's add
a few more
123 456 
Abcd
ABCD
```
///

### Basic usage

By default, tail displays the 10 last lines of a file. Here is the basic syntax:

/// tab | Syntax
```
tail [file_name]
```
///

The following is an example using the `testfile`.

/// tab | Command
```
tail testfile 
```
///
/// tab | Output
```
to carry out a few
operations with tail.
The Tail command
prints the last
10 lines by default
so let's add
a few more
123 456
Abcd
ABCD
```
///

You can use several options for customizing tail output. Here are some of the most popular ones with their long form and functions:

- `-c num` or `--bytes=num`: outputs the last `num` bytes of data.
- `-n num` or `--lines=num`: outputs the last `num` lines of data.
- `-f` or `--follow`: continually outputs new data as it is written to the end of the file.

### Print a specific number of lines

To print a specific number of files, the `-n` option, provided with a number, is used.

/// tab | Command
```
tail -n 3 testfile 
```
///
/// tab | Output
```
123 456
Abcd
ABCD
```
///


### Monitor a file for changes

The `tail` command can be used to monitor a file for changes.  The `--follow` option is used to do this and is very popular for monitoring log files.

As an example two terminals windows will be opened.  In the first terminal, the `testfile` will be monitored using the `tail -f` command.  In the second terminal the `echo` command will be used (coupled with the `>>` append option) to write new data to the same `testfile`.

/// tab | Terminal 1: Command
```
tail -f testfile
```
///
/// tab | Terminal 1: Output before terminal 2 input
```
$ tail -f testfile
to carry out a few
operations with tail.
The Tail command
prints the last
10 lines by default
so let's add
a few more
123 456
Abcd
ABCD
```
///
/// tab | Terminal 2: Command
```
echo 'new string' >> testfile
```
///
/// tab | Terminal 1: Output after terminal 2 input
```
$ tail -f testfile
to carry out a few
operations with tail.
The Tail command
prints the last
10 lines by default
so let's add
a few more
123 456
Abcd
ABCD
new string
```
///

## `vi`/`vim`

The `vi` (or `vim`) editor is the most used command line text editor on UNIX/Linux systems.  It is extremely powerful with many built in features.  It is not easy to use for beginners though.

The following are some high level hints.

### Modes of Operation in the vi editor

There are three modes of operation in vi:

#### Command Mode

This mode is where vi interprets any characters we type as commands and does not display them in the window. This mode allows us to move through a file, and delete, copy, or paste a piece of text. To enter into Command Mode from any other mode, requires pressing the `Esc` key.
When vi starts up, this is the mode it is in.

#### Insert mode

To enter text, you must be in insert mode. To come in insert mode, you simply type `i`. To get out of insert mode, press the `Esc` key, which will put you back into command mode.

#### Escape Mode

Line Mode is invoked by typing a colon `:`, while vi is in Command Mode. The cursor will jump to the last line of the screen and vi will wait for a command. This mode enables you to perform tasks such as saving files and executing commands.


### Commands 

#### Inserting text in Vi Editor

To edit the file, we need to be in the insert mode. There are many ways to enter insert mode from the command mode.

- `i`: Inserts text before current cursor location
- `a`: Insert text after current cursor location 
- `A`: Insert text at the end of current line
- `o`: Creates a new line for text entry below cursor location and switches to insert mode.
- `O`: Creates a new line for text entry above cursor location and switches to insert mode.

#### Save and Exit

Need to press `Esc` key then type `:` before typing the following commands:

- `:q`: Quit.
- `:q!`: Quit without saving changes i.e. discard changes.
- `:wq`: Write and quit (save and exit).




### Searching and replacing

vi also has powerful search and replacement capabilities. to so that we need to be in the Command Mode then enter the Escape Mode 

#### Searching
The syntax for searching is:

/// tab | Syntax
```
:s/string
```
///


Here the `string` represents the text we want to search for 

#### Replacing 
The syntax for replacing one string with another string in the current line is:

/// tab | Syntax
```
:s/pattern/replace/
```
///

Here `pattern` represents the old string and `replace` represents the new string. For example, to replace each occurrence

The syntax for replacing every occurrence of a string in the entire text is similar. The only difference is the addition of a **%** in front of the **s**:

/// tab | Syntax
```
:%s/pattern/replace/
```
///

### Examples

#### Write text into a file

First we need to open a file, we can create a new file directly using vi.

/// tab | Syntax
```
$ vi SreXperts
```
///

Then we need to press the `i` key to enter the Insert mode. we can see that in the last line of the screen the information **--INSERT--** is to inform us that we are in the Insert mode

Now we can write some text

/// tab | Syntax
```
SreXperts is the best
```
///

To save the file we need to go back to the Command Mode, press `Esc` key and then to the Escape mode type a colon `:`. Now, in the Escape mode, type `wq` and press the `Enter` key.


### Search and replace

First we need to open a file using vi.

/// tab | Syntax
```
$ vi SreXperts
```
///

Search for SreXperts in the Escape mode using the command bellow:

/// tab | Search
```
:s/SreXperts
```
///

 Let's replace the string SreXperts in the current line

/// tab | Search and Replace
```
:s/SreXperts/Hackathon/
```
///

in case we had multiple times the string we want to replace, we can replace all of them at once

/// tab | Search and Replace all
```
:%s/Hackathon/SreXperts/
```
///

To save the file we need to go back to the Command Mode, press `Esc` key and then to the Escape mode type a colon `:`. Now, in the Escape mode, type `wq` and press the `Enter` key.

