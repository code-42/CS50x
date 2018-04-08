/**
 * recover.c
 *
 * find JPEGs in file card.raw
 *
 * Usage: ./recover card.raw
 *
 * help from https://stackoverflow.com/questions/25594775
 */

#include <stdio.h>
#include <stdlib.h>
#include <cs50.h>
#include "bmp.h"

// void convertToBit(void* pBuffer, size_t length);

int main(int argc, char *argv[])
{
        // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: recover card.raw\n");
        return 1;
    }

    // assign filename to char*
    char *infile = argv[1];
    // char *buffer;
    int fileLen;

    printf("22. inputs are: %s\n", infile);

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    fseek(inptr, 0, SEEK_END);
    fileLen = ftell(inptr);
    printf("%d\n", fileLen);
    fseek(inptr, 0, SEEK_SET);

    // buffer = (char *)malloc(fileLen+1);
    BYTE buffer[512];

    // initialize jpg variables
    int increment = 0;
    char filename[8];

    // fread(buffer, fileLen, 1, inptr);
    // fread(buffer, 1, 512, inptr);
    int j = 0, k = 0, l = 0, m = 0, n = 0;
    if(inptr != NULL)
    {
        j++;
        while(fread(buffer, 512, 1, inptr) != 0)
        {
            k++;
            for (int i = 1; i < 512; i++){
                if ((buffer[i] == 0xd9) && (buffer[i-1] == 0xff)){
                    printf("found 0xffd9 @ byte %d in block %d\n", i, j);
                }
            }

            if (buffer[0] == 0xff &&
                buffer[1] == 0xd8 &&
                buffer[2] == 0xff &&
                (buffer[3] == 0xe1 || buffer[3] == 0xe0))
            {
                // sprintf(filename, "%.3d.jpg", increment++);
                sprintf(filename, "%03i.jpg", increment++);
                printf("%d filename = %s ", l, filename);
                l++;

                // open new file
                FILE* img = fopen(filename, "w");

                // write first block of 512 bytes, then read next block
                fwrite(buffer, 512, 1, img);

                if(fread(buffer, 512, 1, inptr) == 0)
                {
                    m++;
                    break;
                }


                // copy all information from inpointer to buffer to jpg
                while ((buffer[0] != 0xff  &&
                        buffer[1] != 0xd8  &&
                        buffer[2] != 0xff &&
                        (buffer[3] != 0xe1 && buffer[3] != 0xe0)))
                {
                    n++;
                    // if next byte is NULL break
                    if(fread(buffer, 512, 1, inptr) == 0)
                        break;

                    fread(buffer, 512, 1, inptr);

                    //copies jpg file 1 byte at a time
                    fwrite(buffer, 512, 1, img);
                    // printf("%s ", buffer);

                }

                fclose(img);
            }
        }
    }
    printf("j = %d\nk = %d\nl = %d\nm = %d\nn = %d\n", j, k, l, m, n);

    fclose(inptr);

    // convertToBit(&buffer, fileLen);
    // free(buffer);

}

/*
void convertToBit(void* pBuffer, size_t length)
{
    FILE* pOutput = fopen("file.txt", "w");
    for (size_t i=0; i < length; ++i)
    {
        unsigned char byte = (unsigned char)&pBuffer[i];
        for (int bitIndex=0; bitIndex < 8; ++bitIndex)
        {
            if ((byte & (1 << bitIndex)) != 0)
                fputs("1", pOutput);
            else
                fputs("0", pOutput);

            // fputs("\n", pOutput);
        }
    }

    fclose(pOutput);
}
*/

/*
source https://stackoverflow.com/questions/10531884/write-a-jpg-image-file-in-c
segmentation fault

// convert buffer data to bits and write them to a text file
void convertToBit(void *buffer, int length)
{
    int c=0;
    int SIZE = length * 8;
    unsigned char bits[SIZE + 1];
    unsigned char mask = 1;
    unsigned char byte ;
    int i = 0;
    FILE *bitWRT = fopen("file.txt", "w");

    for (c=0;c<length;c++)
    {
        byte = ((char *)&buffer)[c];

        for(i = 0; i < 8; i++){
            bits[i] = (byte >> i) & mask;
            fprintf(bitWRT, "%d\n", bits[i]);
        }
    }
    fclose(bitWRT);
}
*/