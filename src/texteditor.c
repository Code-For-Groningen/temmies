#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "EditOperation.h"
#include "texteditor.h"
#include "LibStack.h"

TextEditor* createTextEditor(void) {
    TextEditor *editor = malloc(sizeof(*editor));
    // Don't forget to initialize the data structure(s) here
    editor->text = malloc(10 * sizeof(*editor->text));
    editor->length = 0;
    editor->capacity = 10;
    return editor;
}

// Think this is correct
void insertCharacter(TextEditor* editor, int pos, char character) {
    // Implement the insert operation
    if (editor->length == editor->capacity) {
        editor->text = realloc(editor->text, 2 * editor->capacity * sizeof(*editor->text));
        editor->capacity *= 2;
    }
    // Shift all characters to the right
    for (int i = editor->length; i > pos; i--) {
        editor->text[i] = editor->text[i - 1];
    }
    editor->text[pos] = character;
    editor->length++;
}


// This too
void deleteCharacter(TextEditor* editor, int pos) {
    // Implement the delete operation
    if (editor->length == 0) {
        return;
    }
    // Shift all characters to the left
    for (int i = pos; i < editor->length - 1; i++) {
        editor->text[i] = editor->text[i + 1];
    }
    editor->length--;
}

// The issue lies within the mem allocation of the stacks
void undo(TextEditor* editor, Stack* undoStack, Stack* redoStack) {
    // Optional for the bonus exercise
    if (isEmptyStack(*undoStack)) {
        return;
    }
    EditOperation operation = pop(undoStack);
    if (operation.type == INSERT) {
        deleteCharacter(editor, operation.position);
    } else {
        insertCharacter(editor, operation.position, operation.character);
    }
    push(operation, redoStack);    
}

void redo(TextEditor* editor, Stack* undoStack, Stack* redoStack) {
    // Optional for the bonus exercise
    if (isEmptyStack(*redoStack)) {
        return;
    }
    EditOperation operation = pop(redoStack);
    if (operation.type == INSERT) {
        insertCharacter(editor, operation.position, operation.character);
    } else {
        deleteCharacter(editor, operation.position);
    }
    push(operation, undoStack);
}

void destroyTextEditor(TextEditor* editor) {
    // Free the memory allocated for the data structure(s)
    free(editor->text);
    free(editor);
}

void printText(TextEditor* editor) {
    // Handle empty case
    if (editor->length == 0) {
        printf("EMPTY\n");
        return;
    }

    // Print the text stored in the editor
    for (int i = 0; i < editor->length; i++) {
        printf("%c", editor->text[i]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    
    TextEditor* editor = createTextEditor();
    char command;
    int pos;
    char character;

    // Initialize stacks
    Stack undoStack;
    Stack redoStack;
    undoStack = newStack(1);
    redoStack = newStack(1);
    
    while(1) {
        scanf(" %c", &command);
        switch (command) {
            // Insert a character at a given position
            case 'i':
                scanf("%d %c", &pos, &character);
                insertCharacter(editor, pos, character);
                EditOperation operation = {INSERT, character, pos};
                
                // Stack operations
                doubleStackSize(&undoStack);
                push(operation, &undoStack);
                break;
            // Delete a character at a given position
            case 'd':
                scanf("%d", &pos);
                character = editor->text[pos];
                deleteCharacter(editor, pos);
                EditOperation operation1 = {DELETE, character, pos};
                
                doubleStackSize(&undoStack);
                push(operation1, &undoStack);
                break;
            // Undo the last operation
            case 'u':
                undo(editor, &undoStack, &redoStack);
                break;
            // Redo the last operation
            case 'r':
                redo(editor, &undoStack, &redoStack);
                break;
            // Print and quit
            case 'q':
                printText(editor);
                destroyTextEditor(editor);
                freeStack(undoStack);
                freeStack(redoStack);
                return 0;
            // Unknown command
            default:
                printf("Unknown command.\n");
                break;
        }

    }

    
    

    return 0;
}

