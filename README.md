# Escratsou Paper
*Escratsou Paper* is meant to be a simple modification to *datapacks*, by introducing easier syntax to the language.

# Datapacks
## Getting Started
*Escratsou Paper* can generate *datapacks* through `datapack.py`. This file can be ran with two parameters, **input path** and **output path**. These parameters are not needed, but the script will choose the demo pack if parameters are not supplied. The datapack will be generated to the output path (default is the `output` directory).

## ESP Meta Format
The *ESP Meta Format* (*pack.espmeta*) is a file included in the datapack that tells the datapack generator program what generator version to use, datapack format, and the description of the pack.

## Inline Functions
*Inline Functions*, written in Escratsou Paper using `${` and `}$`, runs functions in the same line of **if conditions**, **return statements**, and more! Inline functions can only be used in places where you would usually call functions in the vanilla datapack language.

```mcfunction
execute if entity @s[tag=escratsou] run function ${say Hello!}$
```

## Outside Functions
*Outside Functions*, in the context of *Escratsou Paper*, are functions from *different* files in the *same* datapack. When the datapacks are converted, the names become scrambled; The scrambled names can be fixed with the use of `%{` and `}%`, replacing the name, but not the namespace: `my-cool-namespace:%{my code}%`.

```mcfunction
execute if entity @s[tag=paper] run function namespace:%{other_function}%
```

> [!NOTE]
> Folders are not preserved when converted, leading to all the files to be left inside a *centralized* location, in the `function` directories.
