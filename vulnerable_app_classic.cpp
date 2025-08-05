#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void vulnerable_function(const char* input) {
    char buffer[32];
    strcpy(buffer, input);
}

int main() {
    char* input_buffer = (char*)malloc(2048);
    if (input_buffer == NULL) {
        return 1;
    }

    if (fgets(input_buffer, 2048, stdin) == NULL) {
        free(input_buffer);
        return 1;
    }

    input_buffer[strcspn(input_buffer, "\n")] = 0;

    vulnerable_function(input_buffer);

    free(input_buffer);
    printf("Survived the vulnerable function call.\n");
    return 0;
}