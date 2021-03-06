/**
 * Copies a BMP piece by piece, just because.
 */

#include <stdio.h>
#include <stdlib.h>
#include <cs50.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./copy n infile outfile\n");
        return 1;
    }

    int n = atoi(argv[1]);

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    printf("42. inputs are: %d, %s, %s\n", n, infile, outfile);

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    printf("44. header of %s \n\n", infile);
    printf("45. sizeof(BITMAPFILEHEADER) == %li\n", sizeof(BITMAPFILEHEADER));
    printf("46. sizeof(BITMAPINFOHEADER) == %li\n", sizeof(BITMAPINFOHEADER));
    printf("47. sizeof(RGBTRIPLE) == %li\n", sizeof(RGBTRIPLE));

    printf("48. bf.bfType == %i\n", bf.bfType);
    printf("49. bf.bfSize == %i\n", bf.bfSize);
    printf("50. bf.bfOffBits == %i\n", bf.bfOffBits);
    printf("51. bi.biSize == %i\n", bi.biSize);
    printf("52. bi.biWidth == %i\n", bi.biWidth);
    printf("53. bi.biHeight == %i\n", bi.biHeight);
    printf("55. bi.biBitCount == %i\n", bi.biBitCount);
    printf("57. bi.biSizeImage == %i\n", bi.biSizeImage);

    // determine original_padding for scanlines
    int original_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    printf("81. padding == %i\n", original_padding);

    // original_biWidth and original_biHeight
    long original_biWidth = bi.biWidth;
    long original_biHeight = bi.biHeight;
    printf("84. original_biWidth == %li\n", original_biWidth);
    printf("85. original_biHeight == %li\n", original_biHeight);

    // determine new header values calculated with n
    // new bi.biWidth and bi.biHeight calculated with n
    bi.biWidth = bi.biWidth * n;
    printf("87. bi.biWidth * n == %d\n", bi.biWidth);

    bi.biHeight = bi.biHeight * n;
    printf("90. bi.biHeight * n == %d\n", bi.biHeight);

    // new padding calculated with n
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    // printf("96. padding == %i\n", padding);

    bi.biSizeImage = ((sizeof(RGBTRIPLE) * bi.biWidth) + padding) * abs(bi.biHeight);
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for (int i = 0;  i < labs(original_biHeight); i++)
    {
        eprintf("i.row %d \n", i);
        // declare array to hold pixels
        RGBTRIPLE pixArr[bi.biWidth];
        int x = 0;

        // iterate over pixels in scanline
        for (int j = 0; j < original_biWidth; j++)
        {
            eprintf("j.col %d \n", j);
            // temporary storage
            RGBTRIPLE triple;
            eprintf("sizeof(RGBTRIPLE) == %ld\n", sizeof(RGBTRIPLE));

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
            eprintf("sizeof(RGBTRIPLE) == %ld\n", sizeof(RGBTRIPLE));

            // for each pixel write to array n times
            for (int k = 0; k < n; k++)
            {
                // assign RGB triple to pixArr[]
                pixArr[x] = triple;
                x++;
            }

        }
        // skip over padding, if any
        eprintf("original padding %d \n", original_padding);

        fseek(inptr, original_padding, SEEK_CUR);



eprintf("sizeof(pixArr) == %lu\n", sizeof(pixArr));
eprintf("original_padding == %lu\n", sizeof(original_padding));
eprintf("padding == %lu\n", sizeof(padding));

        // write the array to outfile n times
        for (int row = 0; row < n; row++)
        {
            eprintf("fwrite row %d \n", row);
            fwrite(&pixArr, sizeof(pixArr), 1, outptr);
            // fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);

            // write outfile padding
            for (int k = 0; k < padding; k++)
            {
                eprintf("fwrite padding %d \n", k);
                fputc(0x00, outptr);
            }
        }
    }

    eprintf("header after fwrite to %s \n", outfile);
    // printf("42. inputs are: %d, %s, %s\n", n, infile, outfile);

    printf("179. bf.bfType == %i\n", bf.bfType);
    printf("180. bf.bfSize == %i\n", bf.bfSize);
    printf("181. bf.bfOffBits == %i\n", bf.bfOffBits);
    printf("182. bi.biSize == %i\n", bi.biSize);
    printf("183. bi.biWidth == %i\n", bi.biWidth);
    // xxd -c columns == bi.biWidth * 3 bytes
    printf("185. bi.biHeight == %i\n", bi.biHeight);
    printf("186. bi.biBitCount == %i\n", bi.biBitCount);
    printf("187. bi.biSizeImage == %i\n", bi.biSizeImage);

    // calculate padding for scanlines
    // padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    // printf("191. padding == %i\n", padding);


    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}