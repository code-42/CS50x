// Implements a dictionary's functionality

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <cs50.h>

#include "dictionary.h"

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    fprintf(stderr, "unused reference to word %s\n", word);
    return false;
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // open input file
    // source - pset4
    FILE *inptr = fopen(dictionary, "r");

    // check if something went wrong
    if (inptr == NULL)
    {
        fprintf(stderr, "29. Could not open %s.\n", dictionary);
        return 2;
    }

    // read the dictionary file one char at a time and print to screen
    for (char c = fgetc(inptr); c != EOF; c = fgetc(inptr)){
        // read each char
        if (c != '\n'){
            printf("%c ", c);
        }
    }

    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return 0;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // TODO
    return false;
}
