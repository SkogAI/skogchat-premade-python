# Argc

[![CI](https://github.com/sigoden/argc/actions/workflows/ci.yaml/badge.svg)](https://github.com/sigoden/argc/actions/workflows/ci.yaml)
[![Crates](https://img.shields.io/crates/v/argc.svg)](https://crates.io/crates/argc)

Argc is a powerful Bash framework that simplifies building full-featured CLIs. It lets you define your CLI through comments, focusing on your core logic without dealing with argument parsing, usage text, error messages, and other boilerplate code.

![demo](https://user-images.githubusercontent.com/4012553/228990851-fee5649f-aa24-4297-a924-0d392e0a7400.gif)

## Features

- **Effortless Argument Parsing:**
  - Handles flags, options, positional arguments, and subcommands.
  - Validates user input for robust error handling.
  - Generates information-rich usage text.
  - Maps arguments to corresponding variables.
- **Standalone Bash Script Creation:**
  - Build a bash script that incorporates all functionalities without depending on Argc itself.
- **Cross-shell Autocompletion:**
  - Generate autocompletion scripts for various shells (bash, zsh, fish, powershell, etc.).
- **Man Page Generation:**
  - Automatically create comprehensive man page documentation for your script.
- **Environment Variable Integration:**
  - Define, validate, and bind environment variables to options and positional arguments.
- **Task Automation:**
  - An Bash-based command runner that automates tasks via Argcfile.sh.
- **Cross-Platform Compatibility:**
  - Seamlessly run your Argc-based scripts on macOS, Linux, Windows, and BSD systems.

## Install

### Package Managers

- **Rust Developers:** `cargo install argc`
- **Homebrew/Linuxbrew Users:** `brew install argc`
- **Pacman Users**: `yay -S argc`

#### Pre-built Binaries

Alternatively, download pre-built binaries for macOS, Linux, and Windows from [GitHub Releases](https://github.com/sigoden/argc/releases), extract it, and add the `argc` binary to your `$PATH`.

You can use the following command on Linux, MacOS, or Windows to download the latest release.

```
curl -fsSL https://raw.githubusercontent.com/sigoden/argc/main/install.sh | sh -s -- --to /usr/local/bin
```

### GitHub Actions

[install-binary](https://github.com/sigoden/install-binary) can be used to install argc in a GitHub Actions workflow.

```yaml
  - uses: sigoden/install-binary@v1
    with:
      repo: sigoden/argc
```

## Get Started

Building a command-line program using Argc is a breeze. Just follow these two steps:

**1. Design Your CLI Interface:**

Describe options, flags, positional parameters, and subcommands using comment tags (explained later).

**2. Activate Argument Handling:**

Add this line to your script: `eval "$(argc --argc-eval "$0" "$@")"`. This integrates Argc's parsing magic into your program.

Let's illustrate with an example:

```sh
# @flag -F --foo  Flag param
# @option --bar   Option param
# @option --baz*  Option param (multi-occurs)
# @arg val*       Positional param

eval "$(argc --argc-eval "$0" "$@")"

echo foo: $argc_foo
echo bar: $argc_bar
echo baz: ${argc_baz[@]}
echo val: ${argc_val[@]}
```

Run the script with some sample arguments:

```sh
./example.sh -F --bar=xyz --baz a --baz b v1 v2
```

Argc parses these arguments and creates variables prefixed with `argc_`:

```
foo: 1
bar: xyz
baz: a b
val: v1 v2
```

Just run `./example.sh --help` to see the automatically generated help information for your CLI:

```
USAGE: example [OPTIONS] [VAL]...

ARGS:
  [VAL]...  Positional param

OPTIONS:
  -F, --foo           Flag param
      --bar <BAR>     Option param
      --baz [BAZ]...  Option param (multi-occurs)
  -h, --help          Print help
  -V, --version       Print version

```

With these simple steps, you're ready to leverage Argc and create robust command-line programs!

## Comment Tags

Comment tags are standard Bash comments prefixed with `@` and a specific tag. They provide instructions to Argc for configuring your script's functionalities.

| Tag                                             | Description                           |
| :---------------------------------------------- | ------------------------------------- |
| [`@describe`](./docs/specification.md#describe) | Sets the description for the command. |
| [`@cmd`](./docs/specification.md#cmd)           | Defines a subcommand.                 |
| [`@alias`](./docs/specification.md#alias)       | Sets aliases for the subcommand.      |
| [`@arg`](./docs/specification.md#arg)           | Defines a positional argument.        |
| [`@option`](./docs/specification.md#option)     | Defines an option argument.           |
| [`@flag`](./docs/specification.md#flag)         | Defines a flag argument.              |
| [`@env`](./docs/specification.md#env)           | Defines an environment variable.      |
| [`@meta`](./docs/specification.md#meta)         | Adds metadata.                        |

See [specification](https://github.com/sigoden/argc/blob/main/docs/specification.md) for the grammar and usage of all the comment tags.

## Argc-build

Generate an independent bash script that incorporates all functionalities typically available when the `argc` command is present.

The generated script removes the `argc` dependency, enhances compatibility, and enables deployment in a wider range of environments.

```
argc --argc-build <SCRIPT> [OUTPATH]
```

```sh
argc --argc-build ./example.sh build/

./build/example.sh -h     # The script's functionality does not require the `argc` dependency
```

## Argcscript

Argc is a also command runner built for those who love the efficiency and flexibility of Bash scripting.

Similar to how Makefile define commands for the `make` tool, Argcscript uses an `Argcfile.sh` to store your commands, referred to as "recipes".

**Why Choose Argc for Your Projects?**

- **Leverage Bash Skills:** No need to learn a new language, perfect for Bash aficionados.
- **GNU Toolset Integration:** Utilize familiar tools like awk, sed, grep, find, and others.
- **Environment variables Management**: Load dotenv, document, and validate environment variables effortlessly.
- **Powerful Shell Autocompletion:** Enjoy autocomplete suggestions for enhanced productivity.
- **Cross-Platform Compatibility::** Works seamlessly across Linux, macOS, Windows, and BSD systems.

See [command runner](https://github.com/sigoden/argc/blob/main/docs/command-runner.md) for more details.

![argcscript](https://github.com/sigoden/argc/assets/4012553/42dd99bd-958a-49b7-b87d-585f7bd3b317)

## Completions

Argc automatically provides shell completions for all argc-based scripts.

```
argc --argc-completions <SHELL> [CMDS]...
```

In the following, we use cmd1 and cmd2 as examples to show how to add a completion script for various shells.

```
# bash (~/.bashrc)
source <(argc --argc-completions bash cmd1 cmd2)

# elvish (~/.config/elvish/rc.elv)
eval (argc --argc-completions elvish cmd1 cmd2 | slurp)

# fish (~/.config/fish/config.fish)
argc --argc-completions fish cmd1 cmd2 | source

# nushell (~/.config/nushell/config.nu)
argc --argc-completions nushell cmd1 cmd2 # update config.nu manually according to output

# powershell ($PROFILE)
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
argc --argc-completions powershell cmd1 cmd2 | Out-String | Invoke-Expression

# xonsh (~/.config/xonsh/rc.xsh)
exec($(argc --argc-completions xonsh cmd1 cmd2))

# zsh (~/.zshrc)
source <(argc --argc-completions zsh cmd1 cmd2)

# tcsh (~/.tcshrc)
eval `argc --argc-completions tcsh cmd1 cmd2`
```

The core of all completion scripts is to call `argc --argc-compgen` to obtain completion candidates.

```
$ argc --argc-compgen bash ./example.sh example --
--foo (Flag param)
--bar (Option param)
--baz (Option param (multi-occurs))
--help (Print help)
--version (Print version)
```

So argc is a also completion engine, see [argc-completions](https://github.com/sigoden/argc-completions).

## Manpage

Generate man pages for your argc-based CLI.

```
argc --argc-mangen <SCRIPT> [OUTDIR]
```

```sh
argc --argc-mangen ./example.sh man/

man man/example.1
```

<details>
<summary>

## MacOS

The built-in Bash in macOS is version 3.2 (released in 2007), and the known tools (ls, cp, grep, sed, awk, etc.) are based on BSD.
For better functionality and compatibility, it is recommended to install Bash version 5 and GNU tools.

</summary>

Use `brew` to install Bash and GNU tools:

```sh
brew install bash coreutils gawk gnu-sed grep
```

And update the `PATH` environment variable:

```sh
export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:/opt/homebrew/opt/gawk/libexec/gnubin:/opt/homebrew/opt/gnu-sed/libexec/gnubin:/opt/homebrew/opt/grep/libexec/gnubin:$PATH"
```

</details>

<details>
<summary>

## Windows

The only dependency for `argc` is Bash. Since most developers working on Windows have [Git](https://gitforwindows.org/) installed, which includes Git Bash, you can safely use `argc` and GNU tools (like `grep`, `sed`, `awk`, etc.) in the Windows environment.

</summary>

## Make `.sh` file executable

To execute a `.sh` script file directly like a `.cmd` or `.exe` file, execute the following code in PowerShell.

```ps1
# Add .sh to PATHEXT
[Environment]::SetEnvironmentVariable("PATHEXT", [Environment]::GetEnvironmentVariable("PATHEXT", "Machine") + ";.SH", "Machine")

# Associate the .sh file extension with Git Bash
New-Item -LiteralPath Registry::HKEY_CLASSES_ROOT\.sh
New-ItemProperty -LiteralPath Registry::HKEY_CLASSES_ROOT\.sh -Name "(Default)" -Value "sh_auto_file" -PropertyType String -Force
New-ItemProperty -LiteralPath  Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Classes\sh_auto_file\shell\open\command `
  -Name '(default)' -Value '"C:\Program Files\Git\bin\bash.exe" "%1" %*' -PropertyType String -Force
```

![windows-shell](https://github.com/sigoden/argc/assets/4012553/16af2b13-8c20-4954-bf58-ccdf1bbe23ef)

</details>

## License

Copyright (c) 2023-2024 argc developers.

argc is made available under the terms of either the MIT License or the Apache License 2.0, at your option.

See the LICENSE-APACHE and LICENSE-MIT files for license details.

# Command runner

Argc is a also command runner built for those who love the efficiency and flexibility of Bash scripting.

This guide provides instructions on how to effectively use `argc` for this purpose.

## Create an Argcfile.sh

Commands, called recipes, are stored in a file called argcfile .

Use `--argc-create` to quickly generate an `Argcfile.sh` for your project.

```sh
argc --argc-create build test
```

This creates a basic Argcfile.sh with sample `build` and `test` recipes.

```sh
#!/usr/bin/env bash

set -e

# @cmd
build() {
    echo TODO build
}

# @cmd
test() {
    echo TODO test
}

# See more details at https://github.com/sigoden/argc
eval "$(argc --argc-eval "$0" "$@")"
```

A recipe is a regular shell function with a `@cmd` comment tag above it.

## Handle dependencies

Since recipe are functions, manage dependencies by calling them sequentially within other functions.

```sh
# @cmd
current() { before;
  echo current
after; }

# @cmd
before() {
  echo before
}

# @cmd
after() { 
  echo after
}
```

This example demonstrates how the `current` recipe calls both `before` and `after` recipes.

```
$ argc current
before
current
after
```

## Organize Recipes

Organize related recipes into groups for better readability.

```sh
# @cmd
test() { :; }
# @cmd
test-unit() { :; }
# @cmd
test-bin() { :; }
```

> Valid group formats include: `foo:bar` `foo.bar` `foo@bar`.

## Set default recipe

When invoked without a specific recipe, Argc displays available recipes.

```
$ argc
USAGE: Argcfile.sh <COMMAND>

COMMANDS:
  build
  test

```

Use `main` function to set a default recipe to run automatically.

```sh
# @cmd
build() { :; }

# @cmd
test() { :; }

main() {
  build
}
```

Another way is to use `@meta default-subcommand`

```sh
# @cmd
# @meta default-subcommand
build() { :; }

# @cmd
test() { :; }
```

Remember, you can always use `--help` for detailed help information.

## Aliases

Aliases allow recipes to be invoked on the command line with alternative names:

```sh
# @cmd
# @alias t
test() {
  echo test
}
```

Now you can run the `test` recipe using the alias `t`:

```
argc t
```

## Access positional arguments

Accessed through shell positional variables (`$1`, `$2`, `$@`, `$*` etc.).

```sh
# @cmd
build() {
  echo $1 $2
  echo $@
  echo $*
}
```

```
$ argc build foo bar
foo bar
foo bar
```

## Access Flag/option arguments

Define and use flags/options for more control.

```sh
# @cmd  A simple command
# @flag -f --flag   A flag parameter
# @option -option   A option parameter
# @arg arg          A positional parameter
cmd() {
  echo "flag:    $argc_flag"
  echo "option:  $argc_option"
  echo "arg:     $argc_arg"
}
```

```
$ argc cmd -h
A simple command

USAGE: Argcfile.sh cmd [OPTIONS] [ARG]

ARGS:
  [ARG]  A positional parameter

OPTIONS:
  -f, --flag             A flag parameter
      --option <OPTION>  A option parameter
  -h, --help             Print help

$ argc cmd -f --option foo README.md
flag:    1
option:  foo
arg:     README.md
```

## Load environment variables from dotenv file

Use `@meta dotenv` to load environment variables from a `.env` file.

```sh
# @meta dotenv                                    # Load .env
# @meta dotenv .env.local                         # Load .env.local
```

## Document and Validate environment variables

Define environment variables using `@env`.

```sh
# @env  FOO               A env var
# @env  BAR!              A required env var
# @env  MODE[dev|prod]    A env var with possible values
```

Argc automatically generates help information for environment variables.

By running `argc -h`, you'll see a list of variables with descriptions and any restrictions.

```
$ argc -h
USAGE: Argcfiles.sh

ENVIRONMENTS:
  FOO   A env var
  BAR*  A required env var
  MODE  A env var with possible values [possible values: dev, prod]
```

Argc also validates environment variables as per the `@env` definitions.

If `$BAR` is missing, Argc will report an error:

```
error: the following required environments were not provided:
  BAR$MO
```

For `$MODE`, which has predefined values, Argc verifies the input values and reports errors if they do not match:

```
error: invalid value `abc` for environment variable `MODE`
  [possible values: dev, prod]
```

## Align the project's rootdir

Argc automatically cds into the directory of the Argcfile.sh it finds in the parent hierarchy.

Project directory structure as follows:

```
$ tree /tmp/project

/tmp/project
├── Argcfile.sh
└── src
```

The code of build recipe as follows:

```sh
# @cmd
build() {
    echo $PWD
    echo $ARGC_PWD
}
```

Run the build in the project dir:

```
$ argc build
/tmp/project
/tmp/project
```

Change directory (cd) into the subdirectory and run the build:

```
$ cd src && argc build
/tmp/project
/tmp/project/src
```

When running argc under the subdirectory other than project root,
`PWD` points to the project root, while `ARGC_PWD` points to the current directory.

# Specification

## Comment Tags

### `@describe`

Sets the description for the command.

> **<sup>Syntax</sup>**\
> `@describe` [_description_]

```sh
# @describe A demo CLI
```

### `@cmd`

Defines a subcommand.

> **<sup>Syntax</sup>**\
> `@cmd` [_description_]<sup>?</sup>

```sh
# @cmd Upload a file
upload() {
  echo Run upload
}

# @cmd Download a file
download() {
  echo Run download
}
```

```
USAGE: prog <COMMAND>

COMMANDS:
  upload    Upload a file
  download  Download a file
```

### `@alias`

Sets aliases for the subcommand.

> **<sup>Syntax</sup>**\
> [_name_] (`,` [_name_])<sup>\*</sup>

```sh
# @cmd Run tests
# @alias t,tst
test() {
  echo Run test
}
```

```
USAGE: prog <COMMAND>

COMMANDS:
  test  Run tests [aliases: t, tst]
```

### `@arg`

Defines a positional argument.

> **<sup>Syntax</sup>**\
> `@arg` [_name_] [_modifier_]<sup>?</sup> [_param-value_]<sup>?</sup>
> [_bind-env_]<sup>?</sup>
> [_notation_]<sup>?</sup>
> [_description_]<sup>?</sup>

```sh
# @arg va
# @arg vb!                        required
# @arg vc*                        multi-values
# @arg vd+                        multi-values + required
# @arg vna <PATH>                 value notation
# @arg vda=a                      default
# @arg vdb=`_default_fn`          default from fn
# @arg vca[a|b]                   choices
# @arg vcb[=a|b]                  choices + default
# @arg vcc*[a|b]                  multi-values + choice
# @arg vcd+[a|b]                  required + multi-values + choice
# @arg vfa[`_choice_fn`]          choice from fn
# @arg vfb[?`_choice_fn`]         choice from fn + no validation
# @arg vfc*[`_choice_fn`]         multi-values + choice from fn
# @arg vfd*,[`_choice_fn`]        multi-values + choice from fn + comma-separated list
# @arg vxa~                       capture all remaining args
# @arg vea $$                     bind-env
# @arg veb $BE <PATH>             bind-named-env
```

### `@option`

Defines an option argument.

> **<sup>Syntax</sup>**\
> `@option` [_short_]<sup>?</sup> [_long_] [_modifier_]<sup>?</sup> [_param-value_]<sup>?</sup>
> [_bind-env_]<sup>?</sup>
> [_notations_]<sup>?</sup>
> [_description_]<sup>?</sup>

```sh
# @option    --oa                   
# @option -b --ob                   short
# @option -c                        short only
# @option    --oc!                  required
# @option    --od*                  multi-occurs
# @option    --oe+                  required + multi-occurs
# @option    --of*,                 multi-occurs + comma-separated list
# @option    --ona <PATH>           value notation
# @option    --onb <FILE> <FILE>    two-args value notations
# @option    --onc <CMD> <FILE+>    unlimited-args value notations
# @option    --oda=a                default
# @option    --odb=`_default_fn`    default from fn
# @option    --oca[a|b]             choice
# @option    --ocb[=a|b]            choice + default
# @option    --occ*[a|b]            multi-occurs + choice
# @option    --ocd+[a|b]            required + multi-occurs + choice
# @option    --ofa[`_choice_fn`]    choice from fn
# @option    --ofb[?`_choice_fn`]   choice from fn + no validation
# @option    --ofc*[`_choice_fn`]   multi-occurs + choice from fn
# @option    --ofd*,[`_choice_fn`]  multi-occurs + choice from fn + comma-separated list
# @option    --oxa~                 capture all remaining args
# @option    --oea $$               bind-env
# @option    --oeb $BE <PATH>       bind-named-env
```

### `@flag`

Defines a flag argument. Flag is a special option that does not accept any value.

> **<sup>Syntax</sup>**\
> `@flag` [_short_]<sup>?</sup> [_long_]`*`<sup>?</sup>
> [_bind-env_]<sup>?</sup>
> [_description_]<sup>?</sup>

```sh
# @flag     --fa 
# @flag  -b --fb         short
# @flag  -c              short only
# @flag     --fd*        multi-occurs
# @flag     --ea $$      bind-env
# @flag     --eb $BE     bind-named-env
```

### `@env`

Defines an environment variable.

> **<sup>Syntax</sup>**\
> `@arg` [_NAME_]`!`<sup>?</sup>[_param-value_]<sup>?</sup>
> [_notation_]<sup>?</sup>
> [_description_]<sup>?</sup>

```sh
# @env EA                 optional
# @env EB!                required
# @env EC=true            default
# @env EDA[dev|prod]      choices
# @env EDB[=dev|prod]     choices + default
```

### `@meta`

Adds metadata.

> **<sup>Syntax</sup>**\
> `@meta` [_name_] [_value_]<sup>?</sup>

| syntax                           | scope  | description                                                          |
| :------------------------------- | ------ | :------------------------------------------------------------------- |
| `@meta version <value>`          | any    | Set the version for the command.                                     |
| `@meta author <value>`           | any    | Set the author for the command.                                      |
| `@meta dotenv [<path>]`          | root   | Load a dotenv file from a custom path, if persent.                   |
| `@meta default-subcommand`       | subcmd | Set the current subcommand as the default.                           |
| `@meta require-tools <tool>,...` | any    | Require certain tools to be available on the system.                 |
| `@meta man-section <1-8>`        | root   | Override the section for the man page, defaulting to 1.              |
| `@meta inherit-flag-options`     | root   | Subcommands will inherit the flags/options from their parent.        |
| `@meta combine-shorts`           | root   | Short flags/options can be combined, e.g. `prog -xf => prog -x -f`. |
| `@meta symbol <param>`           | any    | Define a symbolic parameter, e.g. `+toolchain`, `@argument-file`.    |

```sh
# @meta version 1.0.0
# @meta author nobody <nobody@example.com>
# @meta dotenv
# @meta dotenv .env.local
# @meta require-tools git,yq
# @meta man-section 8
# @meta symbol +toolchain[`_choice_fn`]
```

## Syntax parts

### short

 A single character abbreviation for a flag/option.

> **<sup>Syntax</sup>**\
> &nbsp;&nbsp; -[_short-char_] \
> | +[_short-char_]

### long

A descriptive name for a flag/option.

> **<sup>Syntax</sup>**\
> &nbsp; -- [_long-name_] \
> | -[_long-name_] \
> | +[_long-name_]

### modifier

Symbols used to modify param behavior:

> **<sup>Syntax</sup>**\
> &nbsp; `!` \
> | `*` [_separated-char_]<sup>?</sup> \
> | `+` [_separated-char_]<sup>?</sup>

- `!`: The option is required and must be provided.
- `*`: multi-occurs for @option; multi-values for @arg;
- `+`: The option is required and can be used multiple times.

### param-value

Ways to specify values for params:

> **<sup>Syntax</sup>**\
> &nbsp; =[_value_] \
> | =\`[_fn-name_]\` \
> | [[_choices_]] \
> | [=[_choices_]] \
> | [\`[_fn-name_]\`] \
> | [?\`[_fn-name_]\`]

### choices

Define a set of acceptable values for an param

> **<sup>Syntax</sup>**\
> [_value_] (`|` [_value_])<sup>\*</sup>

### notations

Placeholders in help messages and usage instructions:

> **<sup>Syntax</sup>**\
> ([_notation_] )<sup>\*</sup>  [_notation-last_]

### notation

> **<sup>Syntax</sup>**\
> `<` [_value_]`>`

- `FILE`/`PATH`: complete files
- `DIR`: complete directories

### notation-last

> **<sup>Syntax</sup>**\
> `<` [_value_] [_notation-modifier_]<sup>?</sup> `>`

### notation-modifier

Symbols used within the last notation to specify value requirements

> **<sup>Syntax</sup>**\
> &nbsp; `*` \
> | `+` \
> | `?`

- `*`: Zero or more values are allowed.
- `+`: One or more values are allowed.
- `?`: Zero or one value is allowed.

### short-char

A-Z a-z 0-9 `!` `#` `$` `%` `*` `+` `,` `.` `/` `:` `=` `?` `@` `[` `]` `^` `_` `{` `}` `~`

### separated-char

`,` `:` `@` `|` `/`

### bind-env

 Link environment variables to params:

- `$$`: Automatically use the param's name for the environment variable.
- `$`[_NAME_]: Use a specific environment variable name.

### description

Plain text for documentation and usage information

```sh
# @describe Can be multiline 
#
# Extra lines after the comment tag accepts description, which don't start with an `@`,
# are treated as the long description. A line which is not a comment ends the block.
```

[_short_]: #short
[_long_]: #long
[_modifier_]: #modifier
[_param-value_]: #param-value
[_choices_]: #choices
[_notations_]: #notations
[_notation_]: #notation
[_notation-last_]: #notation-last
[_notation-modifier_]: #notation-modifier
[_short-char_]: #short-char
[_separated-char_]: #separated-char
[_bind-env_]: #bind-env
[_description_]: #description
[_name_]: #name
[_long-name_]: #name
[_fn-name_]: #fn-name
[_value_]: #value
[_NAME_]: #name# Variables

Argc streamlines argument parsing in your shell scripts, allowing you to utilize variables seamlessly.

## Shell Variables

You can employ shell variables within your argc-based scripts just like you normally would in Bash. Argc doesn't interfere with their behavior.

```sh
# @cmd
cmd() {
  echo $1 $2  # Accessing positional arguments
  echo "$*"   # All arguments as a single string
  echo "$@"   # All arguments as separate strings
}
```

## Argc-Generated Variables

Argc automatically creates variables corresponding to the options, flags, and positional arguments defined in your script using the `@option`, `@flag`, and `@arg` directives.

```sh
# @option --oa
# @option --ob*  # Multiple values allowed
# @flag   --fa
# @arg va
# @arg vb*

eval "$(argc --argc-eval "$0" "$@")"  # Initializes Argc variables

echo '--oa:' $argc_oa
echo '--ob:' ${argc_ob[@]}  # Accessing multiple values as an array
echo '--fa:' $argc_fa
echo '  va:' $argc_va
echo '  vb:' ${argc_vb[@]}
```

Running `./script.sh --oa a --ob=b1 --ob=b2 --fa foo bar baz` would output:

```
--oa: a
--ob: b1 b2
--fa: 1
  va: foo
  vb: bar baz
```

## Built-in Variables

Argc also provides built-in variables that offer information about the parsing process:

- **`argc__args`**: An array holding all command-line arguments.
- **`argc__positionals`**: An array containing only the positional arguments.
- **`argc__fn`**: The name of the function that will be executed.

**Additional Variables for Completion (Used internally by Argc-Completions):**

- **`argc__cmd_arg_index`**: Index of the command argument within `argc__args`.
- **`argc__cmd_fn`**: Name of the command function.
- **`argc__dash`**: Index of the first em-dash (`--`) within the positional arguments.
- **`argc__option`**: Variable name of the option currently being completed.

These variables are particularly useful when creating custom completion scripts.

## Environment Variables

Several environment variables allow you to tailor Argc's behavior:

**User-Defined:**

- **`ARGC_SHELL_PATH`**: Specifies the path to the shell/bash executable used by Argc.
- **`ARGC_SCRIPT_NAME`**: Overrides the default script filename (Argcfile.sh).
- **`ARGC_COMPGEN_DESCRIPTION`**: Disables descriptions for completion candidates if set to 0 or false.
- **`ARGC_COMPLETIONS_PATH`**: Defines the search path for Argc-based completion scripts.

**Argc-Injected:**

- **`ARGC_PWD`**: Current working directory (available only in Argcfile.sh).

**Argc-Injected (for completion):**
- **`ARGC_OS`**: Operating system type.
- **`ARGC_COMPGEN`**: Indicates whether the script is being used for generating completion candidates (1) or not (0).
- **`ARGC_CWORD`**: The last word in the processed command line.

It's important to distinguish between these two variables:

- **`ARGC_CWORD`**: This variable isolates the final word, regardless of any preceding flags or options. For example, in the command `git --git-dir=git`, `ARGC_CWORD` would be `git`.
- **`ARGC_LAST_ARG`**: This variable captures the entire last argument, including any flags or options attached to it. In the same example, `ARGC_LAST_ARG` would be `--git-dir=git`.

Understanding these variables is key to effectively leveraging Argc's capabilities and creating robust and user-friendly command-line interfaces.

# @describe All kinds of @arg

# @cmd

cmd() {
    _debug "$@"
}

# @cmd

# @alias a

cmd_alias() {
    _debug "$@"
}

# @cmd

# @arg val

cmd_arg() {
    _debug "$@"
}

# @cmd

# @arg val*

cmd_multi_arg() {
    _debug "$@"
}

# @cmd

# @arg val+

cmd_required_multi_arg() {
    _debug "$@"
}

# @cmd

# @arg val

cmd_required_arg() {
    _debug "$@"
}

# @cmd

# @arg val=xyz

cmd_arg_with_default() {
    _debug "$@"
}

# @cmd

# @arg val=`_default_fn`

cmd_arg_with_default_fn() {
    _debug "$@"
}

# @cmd

# @arg val[x|y|z]

cmd_arg_with_choices() {
    _debug "$@"
}

# @cmd

# @arg val[=x|y|z]

cmd_arg_with_choices_and_default() {
    _debug "$@"
}

# @cmd

# @arg val*[x|y|z]

cmd_multi_arg_with_choices() {
    _debug "$@"
}

# @cmd

# @arg val+[x|y|z]

cmd_required_multi_arg_with_choices() {
    _debug "$@"
}

# @cmd

# @arg val[`_choice_fn`]

cmd_arg_with_choice_fn() {
    _debug "$@"
}

# @cmd

# @arg val[?`_choice_fn`]

cmd_arg_with_choice_fn_and_skip_check() {
    _debug "$@"
}

# @cmd

# @arg val![`_choice_fn`]

cmd_required_arg_with_choice_fn() {
    _debug "$@"
}

# @cmd

# @arg val*[`_choice_fn`]

cmd_multi_arg_with_choice_fn() {
    _debug "$@"
}

# @cmd

# @arg val+[`_choice_fn`]

cmd_required_multi_arg_with_choice_fn() {
    _debug "$@"
}

# @cmd

# @arg val*,[`_choice_fn`]

cmd_multi_arg_with_choice_fn_and_comma_sep() {
    _debug "$@"
}

# @cmd

# @arg vals~

cmd_terminaled() {
    _debug "$@"
}

# @cmd

# @arg val <FILE>

cmd_arg_with_notation() {
    _debug "$@"
}

# @cmd

# @arg val1*

# @arg val2*

cmd_two_multi_args() {
    _debug "$@"
}

# @cmd

# @arg val1

# @arg val2+

cmd_one_required_second_required_multi() {
    _debug "$@"
}

# @cmd

# @arg val1

# @arg val2

# @arg val3

cmd_three_required_args() {
    _debug "$@"
}

_debug() {
    ( set -o posix ; set ) | grep ^argc_
    echo "$argc__fn" "$@"
}

_default_fn() {
 echo abc
}

_choice_fn() {
 echo abc
 echo def
 echo ghi
}

eval "$(argc --argc-eval "$0" "$@")"

# @cmd How to bind env to param

# @flag --fa1 $$

# @flag --fa2 $$

# @flag --fa3 $FA

# @flag --fc* $$

# @flag --fd $$

flags() {
    _debug "$@"
}

# @cmd

# @option --oa1 $$

# @option --oa2 $$

# @option --oa3 $OA

# @option --ob! $OB

# @option --oc*, $$

# @option --oda=a $$

# @option --odb=`_default_fn` $$

# @option --oca[a|b] $$

# @option --occ*[a|b] $$

# @option --ofa[`_choice_fn`] $$

# @option --ofd*,[`_choice_fn`] $$

# @option --oxa~ $$

options() {
    _debug "$@"
}

# @cmd

# @arg val $$

cmd_arg1() {
    _debug "$@"
}

# @cmd

# @arg val $VA

cmd_arg2() {
    _debug "$@"
}

# @cmd

# @arg val=xyz $$

cmd_arg_with_default() {
    _debug "$@"
}

# @cmd

# @arg val[x|y|z] $$

cmd_arg_with_choice() {
    _debug "$@"
}

# @cmd

# @arg val[`_choice_fn`] $$

cmd_arg_with_choice_fn() {
    _debug "$@"
}

# @cmd

# @arg val*,[`_choice_fn`] $$

cmd_multi_arg_with_choice_fn_and_comma_sep() {
    _debug "$@"
}

# @cmd

# @arg val1! $$

# @arg val2! $$

# @arg val3! $$

cmd_three_required_args() {
    _debug "$@"
}

# @cmd

# @option --OA $$ <XYZ>

# @arg val $$ <XYZ>

cmd_for_notation() {
    _debug "$@"
}

_debug() {
    ( set -o posix ; set ) | grep ^argc_
    echo "$argc__fn" "$@"
}

_default_fn() {
    echo argc
}

_choice_fn() {
 echo abc
 echo def
 echo ghi
}

eval "$(argc --argc-eval "$0" "$@")"# @describe How to use `@meta combine-shorts`

#

# Mock rm cli

# Examples

# prog -rf dir1 dir2

#

# @meta combine-shorts

# @flag -r --recursive remove directories and their contents recursively

# @flag -f --force ignore nonexistent files and arguments, never prompt

# @arg path* the path to remove

eval "$(argc --argc-eval "$0" "$@")"

_debug() {
    ( set -o posix ; set ) | grep ^argc_
    echo "$argc__fn" "$@"
}

_debug# describe How to use `@meta default-subcommand`

# @cmd Upload a file

# @meta default-subcommand

upload() {
    echo upload "$@"
}

# @cmd Download a file

download() {
    echo download "$@"
}

eval "$(argc --argc-eval "$0" "$@")"# @describe A demo cli

# @cmd Upload a file

# @alias    u

# @arg target!                      File to upload

upload() {
    echo "cmd                       upload"
    echo "arg:  target              $argc_target"
}

# @cmd Download a file

# @alias    d

# @flag     -f --force              Override existing file

# @option   -t --tries <NUM>        Set number of retries to NUM

# @arg      source!                 Url to download from

# @arg      target                  Save file to

download() {
    echo "cmd:                      download"
    echo "flag:   --force           $argc_force"
    echo "option: --tries           $argc_tries"
    echo "arg:    source            $argc_source"
    echo "arg:    target            $argc_target"
}

eval "$(argc --argc-eval "$0" "$@")"

# @describe All kinds of @env

# @meta dotenv

# @env TEST_EA                   optional

# @env TEST_EB!                  required

# @env TEST_EDA=a                default

# @env TEST_EDB=`_default_fn`    default from fn

# @env TEST_ECA[a|b]             choice

# @env TEST_ECB[=a|b]            choice + default

# @env TEST_EFA[`_choice_fn`]    choice from fn

# @cmd

# @env TEST_EA                   override

# @env TEST_NEW                  append

run() {
    _debug
}

main() {
    _debug
}

_debug() {
    printenv | grep ^TEST_ | sort
}

_default_fn() {
    echo argc
}

_choice_fn() {
    echo abc
    echo def
 echo ghi
}

eval "$(argc --argc-eval "$0" "$@")"#/usr/bin/env node
set -e

# @describe How to use argc hooks

#

# Argc supports two hooks

# _argc_before: call before running the command function (after initialized variables)

# _argc_after: call after running the command function

_argc_before() {
  echo before
}

_argc_after() {
  echo after
}

main() {
  echo main
}

eval "$(argc --argc-eval "$0" "$@")"# @describe How to use `@meta inherit-flag-options`

#

# Mock systemctl cli

# Examples

# prog --user start my-service

# prog --user stop my-service

#

# @meta inherit-flag-options

# @flag --user Connect to user service manager

# @flag --no-pager Do not pipe output into a pager

# @option -t --type List units of a particular type

# @option --state List units with particular LOAD or SUB or ACTIVE state

# @cmd Start (activate) one or more units

# @arg UNIT... The unit files to start

start() {
    :;
}

# @cmd Stop (deactivate) one or more units

# @arg UNIT... The unit files to stop

stop() {
    :;
}

eval "$(argc --argc-eval "$0" "$@")"# @describe How to use multiline help text

#

# Extra lines after the comment tag accepts description, which don't start with an `@`

# are treated as the long description. A line which is not a comment ends the block

# @meta version 1.0.0

# @meta author  nobody <nobody@example.com>

# @option --foo[=default|full|auto] Sunshine gleams over hills afar, bringing warmth and hope to every soul, yet challenges await as we journey forth, striving for dreams and joy in abundance. Peaceful rivers whisper secrets gently heard

# * default: enables recommended style components

# * full: enables all available components

# * auto: same as 'default', unless the output is piped

# @option --bar Eager dogs jump quickly over the lazy brown fox, swiftly running past green fields, but only until the night turns dark. Bright stars sparkle clearly above us now

# @arg target Eager dogs jump over quick, lazy foxes behind brown wooden fences around dark, old houses. Happy children laugh as they run through golden wheat fields under blue, sunny skies

# Use '-' for standard input

# @cmd Eager dogs jump quickly over lazy foxes, creating wonderful chaos amid peaceful fields, but few noticed their swift escape beyond tall fences. Swift breezes sway gently through green

#

# Extra lines after the comment tag accepts description, which don't start with an `@`

# are treated as the long description. A line which is not a comment ends the block

cmd() { :; }

eval "$(TERM_WIDTH=${TERM_WIDTH:-`tput cols`} argc --argc-eval "$0" "$@")"# @describe How to use nested subcommands

#

# Mock docker cli

# @cmd

builder() { :; }

# @cmd

builder::ls() { :; }

# @cmd

builder::prune() { :; }

# @cmd

builder::rm() { :; }

# @cmd

builder::imagetools() { :; }

# @cmd

builder::imagetools::create() { :; }

# @cmd

builder::imagetools::inspect() { :; }

eval "$(argc --argc-eval "$0" "$@")"# @describe All kinds of @option and @flag

# @meta combine-shorts

# @cmd All kind of options

# @option    --oa

# @option -b --ob                   short

# @option -c                        short only

# @option    --oc!                  required

# @option    --od*                  multi-occurs

# @option    --oe+                  required + multi-occurs

# @option    --of*,                 multi-occurs + comma-separated list

# @option    --ona <PATH>           value notation

# @option    --onb <FILE> <FILE>    two-args value notations

# @option    --onc <CMD> <FILE+>    unlimited-args value notations

# @option    --oda=a                default

# @option    --odb=`_default_fn`    default from fn

# @option    --oca[a|b]             choice

# @option    --ocb[=a|b]            choice + default

# @option    --occ*[a|b]            multi-occurs + choice

# @option    --ofa[`_choice_fn`]    choice from fn

# @option    --ofb[?`_choice_fn`]   choice from fn + no validation

# @option    --ofc*[`_choice_fn`]   multi-occurs + choice from fn

# @option    --ofd*,[`_choice_fn`]  multi-occurs + choice from fn + comma-separated list

# @option    --oxa~                 capture all remaining args

options() {
    _debug "$@"
}

# @cmd All kind of flags

# @flag     --fa

# @flag  -b --fb         short

# @flag  -c              short only

# @flag     --fd*        multi-occurs

# @flag  -e --fe*        short + multi-occurs

flags() {
    _debug "$@"
}

# @cmd Flags or options with single hyphen

# @flag    -fa

# @flag -b -fb

# @flag    -fd*

# @option  -oa

# @option  -od*

# @option  -ona <PATH>

# @option  -oca[a|b]

# @option  -ofa[`_choice_fn`]

options-one-hyphen() {
    _debug "$@"
}

# @cmd Value notation modifier

# @option --oa <VALUE*>           multi values, zero or more

# @option --ob <VALUE+>           multi values, one or more

# @option --oc <VALUE?>           zero or one

options-notation-modifier() {
    _debug "$@"
}

# @cmd All kind of options

# @option     +oa

# @option +b  +ob                   short

# @option +c                        short only

# @option     +oc!                  required

# @option     +od*                  multi-occurs

# @option     +oe+                  required + multi-occurs

# @option     +ona <PATH>           value notation

# @option     +onb <FILE> <FILE>    two-args value notations

# @option     +onc <CMD> <FILE+>    unlimited-args value notations

# @option     +oda=a                default

# @option     +odb=`_default_fn`    default from fn

# @option     +oca[a|b]             choice

# @option     +ocb[=a|b]            choice + default

# @option     +occ*[a|b]            multi-occurs + choice

# @option     +ocd+[a|b]            required + multi-occurs + choice

# @option     +ofa[`_choice_fn`]    choice from fn

# @option     +ofb[?`_choice_fn`]   choice from fn + no validation

# @option     +ofc*[`_choice_fn`]   multi-occurs + choice from fn

# @option     +ofd*,[`_choice_fn`]  multi-occurs + choice from fn + comma-separated list

# @option     +oxa~                 capture all remaining args

options-plus() {
    _debug "$@"
}

# @cmd All kind of flags

# @flag      +fa

# @flag  +b  +fb         short

# @flag  +c              short only

# @flag      +fd*        multi-occurs

# @flag  +e  +fe*        short + multi-occurs

flags-plus() {
    _debug "$@"
}

# @cmd Mixed `-` and `+` options

# @option +a -a

# @option -b +b

# @option +c --c

options-mixed() {
    _debug "$@"
}

# @cmd Prefixed option

# @option -X-*[`_choice_fn`]       prefixied + multi-occurs + choice from fn

# @option +X-*[`_choice_fn`]       prefixied + multi-occurs + choice from fn

options-prefixed() {
    _debug "$@"
}

# @cmd Prefixed option

# @option -f --follow:[a|b]       assigned + choice

options-assigned() {
    _debug "$@"
}

# @cmd

# @flag   -a

# @flag      --fa

# @flag   -f --fb*

# @flag      -sa

# @flag      -sb*

# @option -e

# @option    --oa

# @option    --ob*

# @option    --oc <DIR>

# @option -o --od <FILE> <FILE>

# @option    --oe*

# @option    --ca[x|y|z]

# @option    --cc[`_choice_fn`]

# @option    --cd[?`_choice_fn`]

# @option    --ce*[`_choice_fn`]

# @option -s -soa

test1() {
    _debug "$@"
}

# @cmd

# @option -a --oa

# @option    --ob+

# @option    --oc+

# @option    --oca![`_choice_fn`]

# @option    --ocb+[`_choice_fn`]

# @option    --occ+,[`_choice_fn`]

test2() {
    _debug "$@"
}

# @cmd

# @option    --oe=val

# @option    --of=`_default_fn`

# @option    --cb[=x|y|z]

test3() {
    _debug "$@"
}

_debug() {
    ( set -o posix ; set ) | grep ^argc_
    echo "$argc__fn" "$@"
}

_default_fn() {
    echo argc
}

_choice_fn() {
    echo abc
    echo def
 echo ghi
}

eval "$(argc --argc-eval "$0" "$@")"#/usr/bin/env bash
set -e

# @describe How to use `--argc-parallel`

#

# Compared with GNU parallel, the biggest advantage of argc-parallel is that it preserves `argc_*` variables

# @cmd

cmd1() {
    sleep 3
    echo cmd1 "$@"
    echo argc_oa: $argc_oa
    echo cmd1 stderr >&2
}

# @cmd

cmd2() {
    sleep 3
    echo cmd2 "$@"
    echo argc_oa: $argc_oa
    echo cmd2 stderr >&2
}

# @cmd

# @option --oa

foo() {
    argc --argc-parallel "$0" cmd1 abc ::: func ::: cmd2
}

# @cmd

# @option --oa

bar() {
    cmd1 abc
    func
    cmd2
}

func() {
    echo func
}

eval "$(argc --argc-eval "$0" "$@")"# Argc Examples

Each of these examples demonstrates one aspect or feature of argc.

- [demo.sh](./demo.sh) - A simple demo script.
- [multiline.sh](./multiline.sh) - how to use multiline help text.
- [nested-commands](./nested-commands.sh) - how to use nested commands.
- [hooks.sh](./hooks.sh) - how to use argc hooks.
- [strict.sh](./strict.sh) - how to use strict mode
- [parallel.sh](./parallel.sh) - how to use `--argc-parallel`.

- [args.sh](./args.sh) - all kinds of `@arg`.
- [options.sh](./options.sh) - all kinds of `@option` and `@flag`.
- [bind-env](./bind-envs.sh) - how to bind env to param.
- [envs.sh](./envs.sh) - all kind of `@env`.

- [default-subcommand](./default-subcommand.sh) - how to use `@meta default-subcommand`.
- [require-tools](./require-tools.sh) - how to use `@meta require-tools`.
- [inherit-flag-options](./inherit-flag-options.sh) - how to use `@meta inherit-flag-options`.
- [combine-short](./combine-shorts.sh) - how to use `@meta combine-shorts`.
- [symbol](./symbol.sh): how to use `@meta symbol`.# @describe how to use `@meta require-tools`

# @meta require-tools awk,sed

# @cmd

# @meta require-tools git

require-git() {
    :;
}

# @cmd

# @meta require-tools not-found

require-not-found() {
    :;
}

eval "$(argc --argc-eval "$0" "$@")"
# !/usr/bin/env bash

set -eu

# @flag      --fa

# @option    --oa

# @option    --of*,                 multi-occurs + comma-separated list

# @option    --oda=a                default

# @option    --oca[a|b]             choice

# @option    --ofa[`_choice_fn`]    choice from fn

# @option    --oxa~                 capture all remaining args

main() {
    ( set -o posix ; set ) | grep ^argc_
    echo "${argc__fn:-}" "$@"
}

_choice_fn() {
    echo abc
    echo def
 echo ghi
}

eval "$(argc --argc-eval "$0" "$@")"# @describe How to use `@meta symbol`

#

# Mock cargo cli

# @meta symbol +toolchain[`_choice_toolchain`]

# @cmd Compile the current package

# @alias b

build () {
    :;
}

# @cmd Analyze the current package and report errors, but don't build object files

# @alias c

check() {
    :;
}

_choice_toolchain() {
    cat <<-'EOF'
stable
beta
nightly
EOF
}

eval "$(argc --argc-eval "$0" "$@")"

