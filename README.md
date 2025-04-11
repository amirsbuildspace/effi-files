# effi-files

## Experimentation

- Still in progress but beats normal storage by 60%, GZIP compression by about 20%, and then XZ is variable.

## Uses:



## Limitations:

- No support for indexing

## TODO:

Version 1 

- support for ascii values to have a max value, but then use a length-prefix value to determine actual size.
- instead of padding each individual row, consider padding the entire content and only pad the last 0 - 7 bits (for 1 byte chunk). Then have an ending byte that says how much was padded, and use that next time we write to the file agian.
- option for no indexing and dynamically sized ascii values using value length prefix
- above impl will allow sequences