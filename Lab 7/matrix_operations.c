#include <stdio.h>
#define MAX 10

void inputMatrix(int mat[MAX][MAX], int r, int c) {
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            printf("Enter element [%d][%d]: ", i, j);
            scanf("%d", &mat[i][j]);
        }
    }
}

void printMatrix(int mat[MAX][MAX], int r, int c) {
    printf("\n");
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            printf("%6d", mat[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

void addMatrix(int A[MAX][MAX], int B[MAX][MAX], int C[MAX][MAX], int r, int c) {
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            C[i][j] = A[i][j] + B[i][j];
        }
    }
}

void subMatrix(int A[MAX][MAX], int B[MAX][MAX], int C[MAX][MAX], int r, int c) {
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            C[i][j] = A[i][j] - B[i][j];
        }
    }
}

void mulMatrix(int A[MAX][MAX], int B[MAX][MAX], int C[MAX][MAX], int r1, int c1, int c2) {
    for (int i = 0; i < r1; i++) {
        for (int j = 0; j < c2; j++) {
            C[i][j] = 0;
            for (int k = 0; k < c1; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

void transpose(int A[MAX][MAX], int T[MAX][MAX], int r, int c) {
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            T[j][i] = A[i][j];
        }
    }
}

int isSymmetric(int A[MAX][MAX], int r, int c) {
    if (r != c) return 0;
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            if (A[i][j] != A[j][i])
                return 0;
        }
    }
    return 1;
}

// Determinant of 2x2 or 3x3 matrix
float determinant(int A[MAX][MAX], int n) {
    float det = 0;
    if (n == 2) {
        det = (A[0][0] * A[1][1]) - (A[0][1] * A[1][0]);
    } else if (n == 3) {
        det = A[0][0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1])
            - A[0][1]*(A[1][0]*A[2][2] - A[1][2]*A[2][0])
            + A[0][2]*(A[1][0]*A[2][1] - A[1][1]*A[2][0]);
    } else {
        printf("Determinant calculation supported only for 2x2 or 3x3.\n");
    }
    return det;
}

// Inverse of 2x2 matrix
void inverse2x2(int A[MAX][MAX]) {
    float det = determinant(A, 2);
    if (det == 0) {
        printf("Matrix not invertible (determinant = 0)\n");
        return;
    }
    float inv[2][2];
    inv[0][0] = A[1][1] / det;
    inv[0][1] = -A[0][1] / det;
    inv[1][0] = -A[1][0] / det;
    inv[1][1] = A[0][0] / det;
    printf("Inverse of the 2x2 matrix:\n");
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            printf("%8.2f", inv[i][j]);
        }
        printf("\n");
    }
}

// Inverse of 3x3 matrix (using adjoint and determinant)
void inverse3x3(int A[MAX][MAX]) {
    float det = determinant(A, 3);
    if (det == 0) {
        printf("Matrix not invertible (determinant = 0)\n");
        return;
    }
    float inv[3][3];
    inv[0][0] = (A[1][1]*A[2][2] - A[1][2]*A[2][1]) / det;
    inv[0][1] = (A[0][2]*A[2][1] - A[0][1]*A[2][2]) / det;
    inv[0][2] = (A[0][1]*A[1][2] - A[0][2]*A[1][1]) / det;
    inv[1][0] = (A[1][2]*A[2][0] - A[1][0]*A[2][2]) / det;
    inv[1][1] = (A[0][0]*A[2][2] - A[0][2]*A[2][0]) / det;
    inv[1][2] = (A[0][2]*A[1][0] - A[0][0]*A[1][2]) / det;
    inv[2][0] = (A[1][0]*A[2][1] - A[1][1]*A[2][0]) / det;
    inv[2][1] = (A[0][1]*A[2][0] - A[0][0]*A[2][1]) / det;
    inv[2][2] = (A[0][0]*A[1][1] - A[0][1]*A[1][0]) / det;

    printf("Inverse of the 3x3 matrix:\n");
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%8.2f", inv[i][j]);
        }
        printf("\n");
    }
}

int main() {
    int A[MAX][MAX], B[MAX][MAX], C[MAX][MAX], T[MAX][MAX];
    int r1, c1, r2, c2, choice;
    float det = 0.0;

    printf("Enter rows and columns of Matrix A: ");
    scanf("%d %d", &r1, &c1);
    printf("Enter rows and columns of Matrix B: ");
    scanf("%d %d", &r2, &c2);

    if (r1 > MAX || c1 > MAX || r2 > MAX || c2 > MAX) {
        printf("Matrix size too large!\n");
        return 0;
    }

    printf("Enter elements for Matrix A:\n");
    inputMatrix(A, r1, c1);
    printf("Enter elements for Matrix B:\n");
    inputMatrix(B, r2, c2);

    while (1) {
        printf("\n==== MATRIX MENU ====\n");
        printf("1. Add\n2. Subtract\n3. Multiply\n4. Transpose\n5. Symmetric Check\n");
        printf("6. Determinant\n7. Inverse (2x2 or 3x3)\n8. Exit\nChoice: ");
        scanf("%d", &choice);

        if (choice == 1) {
            if (r1 == r2 && c1 == c2) {
                addMatrix(A, B, C, r1, c1);
                printf("A + B = \n");
                printMatrix(C, r1, c1);
            } else {
                printf("Addition not possible (dimension mismatch)\n");
            }
        } else if (choice == 2) {
            if (r1 == r2 && c1 == c2) {
                subMatrix(A, B, C, r1, c1);
                printf("A - B = \n");
                printMatrix(C, r1, c1);
            } else {
                printf("Subtraction not possible.\n");
            }
        } else if (choice == 3) {
            if (c1 == r2) {
                mulMatrix(A, B, C, r1, c1, c2);
                printf("A x B = \n");
                printMatrix(C, r1, c2);
            } else {
                printf("Multiplication not possible.\n");
            }
        } else if (choice == 4) {
            transpose(A, T, r1, c1);
            printf("Transpose of A:\n");
            printMatrix(T, c1, r1);
        } else if (choice == 5) {
            if (isSymmetric(A, r1, c1))
                printf("Matrix A is symmetric.\n");
            else
                printf("Matrix A is not symmetric.\n");
        } else if (choice == 6) {
            if (r1 == c1 && (r1 == 2 || r1 == 3)) {
                det = determinant(A, r1);
                printf("Determinant of A = %.2f\n", det);
            } else {
                printf("Determinant supported only for 2x2 or 3x3.\n");
            }
        } else if (choice == 7) {
            if (r1 == c1 && r1 == 2)
                inverse2x2(A);
            else if (r1 == c1 && r1 == 3)
                inverse3x3(A);
            else
                printf("Inverse supported only for 2x2 or 3x3.\n");
        } else if (choice == 8) {
            printf("Exiting...\n");
            break;
        } else {
            printf("Invalid choice. Try again.\n");
        }
    }

    return 0;
}
