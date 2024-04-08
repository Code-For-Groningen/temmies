#ifndef TEXTEDITOR_H
#define TEXTEDITOR_H

#include "LibStack.h"

typedef struct TextEditor {
    // Store the data structure in here
    char *text;
    int length;
    int capacity;
} TextEditor;

#endif

